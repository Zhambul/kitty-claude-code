# Copyright (c) 2026 Zhambyl Yermagambet
"""Update stored session data after a canonical event."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from core.repository import RepositoryQueries
from domain.event_session import SessionStarted
from harness.contract import CanonicalEventReaction
from harness.models.session import Session

if TYPE_CHECKING:
    from domain.event_base import CanonicalEvent, EventPayload
    from repository.contract.sessions import SessionRepository


def _has_session_identity(
    canonical_event: CanonicalEvent[EventPayload],
    session_started: SessionStarted | None,
) -> bool:
    return (
        session_started is not None
        or canonical_event.terminal_window_id is not None
        or canonical_event.harness_process_id is not None
    )


def _harness_process_id(
    canonical_event: CanonicalEvent[EventPayload],
    session: Session,
    session_started: SessionStarted | None,
) -> int | None:
    live_start = session_started is not None and (
        canonical_event.terminal_window_id is not None or canonical_event.harness_process_id is not None
    )
    if live_start:
        return canonical_event.harness_process_id
    return canonical_event.harness_process_id or session.harness_process_id


class SessionUpsertCanonicalEventReaction(CanonicalEventReaction):
    """Write and update the stored session.

    A session-start event supplies the first identity and location. A later
    event can update the live terminal and process values after a resume.
    """

    def __init__(
        self,
        session_repository: SessionRepository,
        repository_queries: RepositoryQueries | None = None,
    ) -> None:
        """Initialize the object."""
        self.sessions = session_repository
        self.repositories = repository_queries or RepositoryQueries()

    def react(self, canonical_event: CanonicalEvent[EventPayload]) -> None:
        """Update the session that owns the event."""
        payload = canonical_event.payload
        started = payload if isinstance(payload, SessionStarted) else None
        if not _has_session_identity(canonical_event, started):
            return
        session = self._session(canonical_event, started)
        if session is None:
            return
        self.sessions.save(
            canonical_event.harness,
            replace(
                session,
                terminal_window_id=(canonical_event.terminal_window_id or session.terminal_window_id),
                harness_process_id=_harness_process_id(canonical_event, session, started),
                project_directory=self._project_directory(session, started),
            ),
        )

    def _session(
        self,
        canonical_event: CanonicalEvent[EventPayload],
        session_started: SessionStarted | None,
    ) -> Session | None:
        session = self.sessions.find(canonical_event.session_id)
        if session is not None or session_started is None:
            return session
        return Session(
            session_id=canonical_event.session_id,
            lead_actor_id=canonical_event.actor_id,
            source_reference=session_started.source_reference,
            working_directory=session_started.working_directory or None,
            project_directory=(self.repositories.project_directory(session_started.working_directory) or None),
        )

    def _project_directory(
        self,
        session: Session,
        session_started: SessionStarted | None,
    ) -> str | None:
        if session.project_directory is not None:
            return session.project_directory
        working_directory = (
            session.working_directory or "" if session_started is None else session_started.working_directory
        )
        return self.repositories.project_directory(working_directory) or None
