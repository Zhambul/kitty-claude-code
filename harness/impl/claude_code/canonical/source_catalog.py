# Copyright (c) 2026 Zhambyl Yermagambet
"""Assemble and cache Claude Code raw-event sources."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from domain import ids as domain_ids
from harness import contract as harness_contract
from harness.impl.claude_code import model
from harness.impl.claude_code.canonical import task_sources, transcript, transcript_paths, transcript_sources
from harness.impl.claude_code.canonical.idle_event_source import ClaudeTeammateIdleRawEventSource
from harness.impl.claude_code.canonical.transcript_event_source import ClaudeTranscriptRawEventSource
from harness.models import raw_events as raw_event_models

if TYPE_CHECKING:
    from harness.models import session as session_models

TRANSCRIPT_SUFFIX = ".jsonl"


@dataclass(frozen=True)
class ClaudeSessionSources:
    """Represent cached Claude session sources."""

    session_id: domain_ids.SessionId
    source_reference: str
    config_directory: str
    child_directory_marker: tuple[int, int] | None
    sources: tuple[harness_contract.HarnessRawEventSource, ...]


class ClaudeRawEventSources(harness_contract.HarnessRawEventSources):
    """Represent Claude raw event sources."""

    def __init__(self, configuration_directory: str) -> None:
        """Initialize the Claude Code source catalog."""
        self.configuration_directory = configuration_directory
        self._sessions: list[ClaudeSessionSources] = []

    def release_session(self, session_id: domain_ids.SessionId) -> None:
        """Release transcript readers for one finished session."""
        self._sessions = [cached for cached in self._sessions if cached.session_id != session_id]

    def for_session(self, session: session_models.Session) -> tuple[harness_contract.HarnessRawEventSource, ...]:
        """Return raw-event sources for one Claude session.

        Returns:
            The raw-event sources.

        """
        if not transcript_paths.owns(session.source_reference):
            return ()
        transcript_base = session.source_reference.removesuffix(TRANSCRIPT_SUFFIX)
        child_directory = Path(transcript_base) / transcript.AGENT_SUBDIR
        child_directory_marker = _directory_marker(child_directory)
        previous = self._cached_session(session)
        if previous is not None and previous.child_directory_marker == child_directory_marker:
            return previous.sources
        sources = self._session_sources(session, child_directory)
        self._store_session(session, child_directory_marker, sources, previous)
        return sources

    def _cached_session(self, session: session_models.Session) -> ClaudeSessionSources | None:
        return next(
            (
                source_session
                for source_session in self._sessions
                if source_session.session_id == session.session_id
                and source_session.source_reference == session.source_reference
                and source_session.config_directory == self.configuration_directory
            ),
            None,
        )

    def _session_sources(
        self,
        session: session_models.Session,
        child_directory: Path,
    ) -> tuple[harness_contract.HarnessRawEventSource, ...]:
        sources: list[harness_contract.HarnessRawEventSource] = [
            ClaudeTranscriptRawEventSource(session.source_context),
            ClaudeTeammateIdleRawEventSource(session.source_context),
            task_sources.ClaudeTaskRawEventSource(session, self.configuration_directory),
        ]
        for child_path in sorted(child_directory.glob("agent-*.jsonl")):
            child_source = _child_source(session, child_path)
            if child_source is not None:
                sources.append(child_source)
        return tuple(sources)

    def _store_session(
        self,
        session: session_models.Session,
        child_directory_marker: tuple[int, int] | None,
        sources: tuple[harness_contract.HarnessRawEventSource, ...],
        claude_session_sources: ClaudeSessionSources | None,
    ) -> None:
        if claude_session_sources is not None:
            self._sessions.remove(claude_session_sources)
        self._sessions.append(
            ClaudeSessionSources(
                session.session_id,
                session.source_reference,
                self.configuration_directory,
                child_directory_marker,
                sources,
            ),
        )


def _directory_marker(directory: Path) -> tuple[int, int] | None:
    try:
        status = directory.stat()
    except OSError:
        return None
    return status.st_ino, status.st_mtime_ns


def _child_source(
    session: session_models.Session,
    child_path: Path,
) -> harness_contract.HarnessRawEventSource | None:
    actor_id = transcript_sources.child_actor_id(child_path)
    if actor_id is None:
        return None
    role = (
        "teammate"
        if model.agent_meta(session.source_reference, actor_id).task_kind == "in_process_teammate"
        else "child"
    )
    context = raw_event_models.RawEventSourceContext(
        session_id=session.session_id,
        lead_actor_id=session.lead_actor_id,
        actor_id=actor_id,
        parent_actor_id=session.lead_actor_id,
        source_reference=str(child_path),
    )
    return ClaudeTranscriptRawEventSource(context, role)
