# Copyright (c) 2026 Zhambyl Yermagambet
"""Build canonical events and synthetic raw events."""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass
from typing import TYPE_CHECKING

from domain.event_base import CanonicalEvent, EventPayload
from domain.ids import (
    CanonicalEventIdentity,
    HarnessName,
    RawEventId,
    TurnId,
    stable_event_id,
)
from domain.shells import shell_output_source_key
from harness.models.raw_events import (
    OUTPUT_LOCATION_SOURCE_TYPE,
    RawEvent,
    RawEventSourceContext,
)

if TYPE_CHECKING:
    from domain import event_actor, event_session, event_shell, event_work


@dataclass(frozen=True)
class CanonicalEventDraft:
    """Declare the canonical fact to build from a raw observation."""

    subject_type: str
    subject_id: str
    phase: str
    event_payload: EventPayload
    turn_id: TurnId | None = None
    occurred_at: float | None = None


def plan_resolution_phase(plan_resolved: event_work.PlanResolved) -> str:
    """Return the identity of one reported plan revision.

    Returns:
        The stable phase identity.

    """
    revision = hashlib.sha256(
        "\0".join(
            (
                str(plan_resolved.state),
                plan_resolved.feedback or "",
                "edited" if plan_resolved.edited else "unchanged",
            ),
        ).encode("utf-8"),
    ).hexdigest()
    return f"resolved:{revision}"


def canonical_event(
    raw_event: RawEvent,
    canonical_event_draft: CanonicalEventDraft,
) -> CanonicalEvent[EventPayload]:
    """Build one canonical fact from one raw observation.

    Returns:
        The canonical event.

    """
    return CanonicalEvent(
        event_id=stable_event_id(
            CanonicalEventIdentity(
                harness=raw_event.harness,
                session_id=raw_event.session_id,
                actor_id=raw_event.actor_id,
                subject_type=canonical_event_draft.subject_type,
                subject_id=canonical_event_draft.subject_id,
                phase=canonical_event_draft.phase,
            ),
        ),
        session_id=raw_event.session_id,
        actor_id=raw_event.actor_id,
        turn_id=canonical_event_draft.turn_id,
        parent_actor_id=raw_event.parent_actor_id,
        harness=raw_event.harness,
        occurred_at=canonical_event_draft.occurred_at,
        terminal_window_id=raw_event.terminal_window_id,
        harness_process_id=raw_event.harness_process_id,
        payload=canonical_event_draft.event_payload,
    )


def session_run_started_events(
    raw_event: RawEvent,
    session_started: event_session.SessionStarted,
    actor_started: event_actor.ActorStarted,
    *,
    occurred_at: float | None = None,
) -> tuple[CanonicalEvent[EventPayload], CanonicalEvent[EventPayload]]:
    """Build the two facts that start one native session run.

    Returns:
        The session and actor run events.

    """
    run_id = str(raw_event.terminal_window_id or raw_event.source_position)
    return (
        canonical_event(
            raw_event,
            CanonicalEventDraft(
                "session_run",
                run_id,
                "started",
                session_started,
                occurred_at=occurred_at,
            ),
        ),
        canonical_event(
            raw_event,
            CanonicalEventDraft(
                "actor_run",
                f"{raw_event.actor_id}:{run_id}",
                "started",
                actor_started,
                occurred_at=occurred_at,
            ),
        ),
    )


def session_run_finished_event(
    raw_event: RawEvent,
    session_finished: event_session.SessionFinished,
) -> CanonicalEvent[EventPayload]:
    """Build the finish fact for one native session run.

    Returns:
        The canonical event.

    """
    run_id = str(raw_event.terminal_window_id or raw_event.source_position)
    return canonical_event(
        raw_event,
        CanonicalEventDraft("session_run", run_id, "finished", session_finished),
    )


def output_location_raw_event(
    raw_event_source_context: RawEventSourceContext,
    harness: HarnessName,
    shell_output_located: event_shell.ShellOutputLocated,
    payload: bytes,
) -> RawEvent:
    """Build one shell output location observation.

    Returns:
        The raw event.

    """
    source_key = shell_output_source_key(shell_output_located.source_path)
    return RawEvent(
        raw_event_id=RawEventId(
            f"{harness}:output_location:{raw_event_source_context.session_id}:"
            f"{shell_output_located.shell_id}:{source_key}",
        ),
        harness=harness,
        source_type=OUTPUT_LOCATION_SOURCE_TYPE,
        source_name=shell_output_located.source_path,
        source_position="located",
        session_id=raw_event_source_context.session_id,
        actor_id=raw_event_source_context.actor_id,
        parent_actor_id=raw_event_source_context.parent_actor_id,
        observed_at=time.time(),
        encoding="json",
        payload=payload,
        source_identity=(
            f"{harness}:output_location:{raw_event_source_context.session_id}:"
            f"{shell_output_located.shell_id}:{source_key}:directive"
        ),
    )
