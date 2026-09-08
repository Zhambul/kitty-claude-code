# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide foundation test interpreter."""

from __future__ import annotations

from tests import canonical_foundation_components as foundation_components, foundation_dependencies

OPEN_ACTION = "open"
type TerminalCall = (
    tuple[str, foundation_dependencies.domain.domain_ids.SessionId]
    | tuple[
        str, foundation_dependencies.domain.domain_ids.SessionId, foundation_dependencies.domain.domain_ids.WindowId,
    ]
    | tuple[str, foundation_dependencies.domain.domain_ids.WindowId, int | None, str]
)


@foundation_dependencies.standard.dataclass
class InterpreterStorage:
    """Keep the repositories used by one test interpreter."""

    sessions: foundation_dependencies.repository.SqliteSessionRepository
    recorder: foundation_dependencies.repository.SqliteRawEventRepository
    store: foundation_dependencies.repository.SqliteCanonicalEventRepository
    shell_output: foundation_dependencies.repository.SqliteShellOutputRepository


def provenance(
    store: foundation_dependencies.repository.SqliteCanonicalEventRepository,
    canonical_event: foundation_dependencies.domain.event_base.CanonicalEvent,
) -> tuple[foundation_dependencies.domain.domain_ids.RawEventId, ...]:
    """Read the raw observations used to build a committed fact.

    Returns:
        The raw event identifiers stored with the canonical event.

    """
    stored = store.find(canonical_event.event_id)
    assert stored is not None
    return stored.raw_event_ids


class ReactionLoopOptions(foundation_dependencies.standard.typing.TypedDict, total=False):
    """Contain optional reaction loop test services."""

    terminal: foundation_components.reaction.SessionPaneController | None
    interrupts: foundation_dependencies.engine.InterruptRegistry | None
    controls: foundation_dependencies.engine.harness_contract.HarnessReactorContext | None
    audit: foundation_dependencies.audit.AuditRecorder | None


def row_from_insert(
    insert_row: foundation_components.facts.CanonicalEventInsertRow, cursor: int = 1,
) -> foundation_components.facts.CanonicalEventRow:
    """Return the stored row for canonical-event insert values.

    The database adds the cursor to the insert values.

    Returns:
        The stored row for canonical-event insert values.

    """
    return foundation_components.facts.CanonicalEventRow(
        cursor=cursor,
        event_id=insert_row.event_id,
        schema_version=insert_row.schema_version,
        event_type=insert_row.event_type,
        session_id=insert_row.session_id,
        actor_id=insert_row.actor_id,
        turn_id=insert_row.turn_id,
        parent_actor_id=insert_row.parent_actor_id,
        harness=insert_row.harness,
        occurred_at=insert_row.occurred_at,
        terminal_window_id=insert_row.terminal_window_id,
        harness_process_id=insert_row.harness_process_id,
        accepted_at=insert_row.accepted_at,
        payload=insert_row.payload,
    )


def watchable_session_ids(sessions: foundation_dependencies.repository.SqliteSessionRepository) -> set[str]:
    """Read identifiers for sessions that can be watched.

    Returns:
        The distinct session identifiers as strings.

    """
    return {str(session.session_id) for session in sessions.watchable()}


def stored_reason(
    stored: foundation_dependencies.domain.event_base.CanonicalEvent[
        foundation_dependencies.domain.event_base.EventPayload
    ],
) -> str | None:
    """Read the reason from a session finish event.

    Returns:
        The stored reason, which can be None.

    """
    assert isinstance(stored.payload, foundation_dependencies.domain.event_session.SessionFinished)
    return stored.payload.reason


class RecordingTerminal:
    """Represent recording terminal."""

    def __init__(self) -> None:
        """Create an empty terminal call record."""
        self.calls: list[TerminalCall] = []

    def close_session_panes(
        self, session_id: foundation_dependencies.domain.domain_ids.SessionId,
    ) -> foundation_components.adapter.SessionTerminalResult:
        """Record a request to close the session panes.

        Returns:
            A successful terminal result.

        """
        self.calls.append(("close", session_id))
        return foundation_components.adapter.SessionTerminalResult(succeeded=True)

    def session_panes_are_open(self, session_id: foundation_dependencies.domain.domain_ids.SessionId) -> bool:
        """Check whether an open request was recorded for the session.

        Returns:
            True if an open request exists, even if a close request follows it.

        """
        open_calls = [call for call in self.calls if call[0] == OPEN_ACTION]
        return any(call[1] == session_id for call in open_calls)

    def open_session_panes(
        self, request: foundation_components.adapter.SessionPaneRequest,
    ) -> foundation_components.adapter.SessionTerminalResult:
        """Record a request to open the session panes.

        Returns:
            A successful terminal result.

        """
        self.calls.append((OPEN_ACTION, request.session_id, request.anchor_window_id))
        return foundation_components.adapter.SessionTerminalResult(succeeded=True)

    def window_hosts_process(
        self, window_id: foundation_dependencies.domain.domain_ids.WindowId, process_id: int | None, process_name: str,
    ) -> bool:
        """Record a request to check window process ownership.

        Returns:
            True for every ownership request.

        """
        self.calls.append(("ownership", window_id, process_id, process_name))
        return True
