# Copyright (c) 2026 Zhambyl Yermagambet
"""Translate Claude actor, task, and compaction hooks."""

from __future__ import annotations

from typing import TYPE_CHECKING

from domain import event_actor, event_telemetry
from domain.messaging import ActorRole
from harness.impl.claude_code.canonical import hook_lifecycle, records
from harness.impl.claude_code.canonical.support import event
from harness.impl.claude_code.canonical.tasks import task_hook_event
from harness.models.raw_event_builders import CanonicalEventDraft

if TYPE_CHECKING:
    from domain.event_base import CanonicalEvent, EventPayload
    from harness.models.raw_events import RawEvent
    from harness.models.selections import SelectionSemantics


def actor_hook_events(
    raw_event: RawEvent,
    hook: records.HookPayload,
    selection_semantics: SelectionSemantics,
) -> list[CanonicalEvent[EventPayload]]:
    """Translate an actor, task, or compaction hook.

    Returns:
        The translated events.

    """
    hook_name = hook.hook_event_name or ""
    native_identity = str(hook.hook_event_id or hook.uuid or raw_event.source_position)
    if hook_name == "SubagentStart":
        return _subagent_start_events(raw_event, hook)
    if hook_name == "SubagentStop":
        return [
            event(
                raw_event,
                CanonicalEventDraft(
                    "actor",
                    str(raw_event.actor_id),
                    "finished",
                    event_actor.ActorFinished(None),
                ),
            ),
            *hook_lifecycle.effort_report(
                raw_event,
                hook,
                selection_semantics,
            ),
        ]
    if hook_name in {"TaskCreated", "TaskCompleted"}:
        return [task_hook_event(raw_event, hook)]
    return _compaction_hook_events(raw_event, hook_name, native_identity)


def _compaction_hook_events(
    raw_event: RawEvent,
    hook_name: str,
    native_identity: str,
) -> list[CanonicalEvent[EventPayload]]:
    if hook_name == "PreCompact":
        return [
            event(
                raw_event,
                CanonicalEventDraft(
                    "compaction",
                    native_identity,
                    "started",
                    event_telemetry.CompactionStarted(None),
                ),
            ),
        ]
    return []


def _subagent_start_events(
    raw_event: RawEvent,
    hook: records.HookPayload,
) -> list[CanonicalEvent[EventPayload]]:
    actor_id = raw_event.actor_id
    role = ActorRole.TEAMMATE if raw_event.source_type == "teammate_hook" else ActorRole.CHILD
    events = [
        event(
            raw_event,
            CanonicalEventDraft(
                "actor",
                str(actor_id),
                "started",
                event_actor.ActorStarted(str(actor_id), role),
            ),
        ),
    ]
    if hook.agent_type:
        events.append(
            event(
                raw_event,
                CanonicalEventDraft(
                    "actor",
                    str(actor_id),
                    "name",
                    event_actor.ActorNameChanged(str(hook.agent_type)),
                ),
            ),
        )
    return events
