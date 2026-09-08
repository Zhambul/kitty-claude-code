# Copyright (c) 2026 Zhambyl Yermagambet
"""Application query for sessions offered by the resume picker."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import islice
from typing import TYPE_CHECKING, Protocol

from domain.ids import HarnessName, SessionId
from domain.references import AccountReference, ModelReference

if TYPE_CHECKING:
    from collections.abc import Iterator

    from core.repository import RepositoryQueries
    from domain.session_state import SessionData, SessionFacts
    from harness.models.probe import (
        TerminalSessionState,
    )
    from repository.contract.session_data import SessionDataRepository

UNKNOWN_ACTIVITY_TIME = float(0)


class TerminalSessionReader(Protocol):
    """Read current terminal state for one session."""

    def state(self, session_id: SessionId) -> TerminalSessionState:
        """Return current terminal state for one session."""
        ...


@dataclass(frozen=True)
class ResumableSession:
    """Describe one session that the user can resume."""

    session_id: SessionId
    title: str | None
    last_activity_at: float
    active: bool
    harness: HarnessName
    model: ModelReference | None
    effort: str | None
    account: AccountReference | None


class ResumableSessionService:
    """Select recent sessions for the resume picker."""

    def __init__(
        self,
        session_data_repository: SessionDataRepository,
        terminal_session_reader: TerminalSessionReader,
        repository_queries: RepositoryQueries,
        result_limit: int,
    ) -> None:
        """Create a query service with session and terminal readers."""
        self.read_model = session_data_repository
        self.terminal = terminal_session_reader
        self.repositories = repository_queries
        self.result_limit = result_limit

    def sessions_for(
        self,
        working_directory: str,
        search: str | None,
    ) -> tuple[ResumableSession, ...]:
        """Return recent matching sessions for one working directory.

        Returns:
            Recent matching sessions for one working directory.

        """
        requested_directory = self.repositories.canonical_directory(working_directory)
        if not requested_directory:
            return ()
        search_text = (search or "").strip().lower()
        matching_sessions = self._matching_sessions(
            requested_directory,
            search_text,
        )
        return tuple(self._resumable(session_data) for session_data in islice(matching_sessions, self.result_limit))

    def _matching_sessions(
        self,
        requested_directory: str,
        search_text: str,
    ) -> Iterator[SessionData]:
        ordered_sessions = sorted(
            self.read_model.visible(),
            key=_last_activity,
            reverse=True,
        )
        for session_data in ordered_sessions:
            summary = session_data.session
            if self._matches_directory(summary, requested_directory) and _matches_search(
                summary,
                search_text,
            ):
                yield session_data

    def _matches_directory(self, session_facts: SessionFacts, requested_directory: str) -> bool:
        session_directory = self.repositories.canonical_directory(
            session_facts.working_directory or "",
        )
        return session_directory == requested_directory

    def _resumable(self, session_data: SessionData) -> ResumableSession:
        summary = session_data.session
        lead_actor = next(
            (actor for actor in session_data.actors if actor.actor_id == summary.lead_actor_id),
            None,
        )
        return ResumableSession(
            session_id=summary.session_id,
            title=summary.title,
            last_activity_at=_last_activity(session_data),
            active=self.terminal.state(summary.session_id).window_id is not None,
            harness=summary.harness,
            model=None if lead_actor is None else lead_actor.model,
            effort=None if lead_actor is None else lead_actor.effort,
            account=summary.account,
        )


def _last_activity(session_data: SessionData) -> float:
    return session_data.last_activity_at or session_data.session.started_at or UNKNOWN_ACTIVITY_TIME


def _matches_search(session_facts: SessionFacts, search_text: str) -> bool:
    if not search_text:
        return True
    if search_text in str(session_facts.session_id).lower():
        return True
    return session_facts.title is not None and search_text in session_facts.title.lower()
