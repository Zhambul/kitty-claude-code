# Copyright (c) 2026 Zhambyl Yermagambet
"""Claude Code task translation from task snapshots and lifecycle hooks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from domain.event_work import TaskChanged
from domain.work_state import TaskState
from harness.impl.claude_code.canonical.support import event
from harness.impl.claude_code.ids import (
    ClaudeCodeActorId,
    ClaudeCodeTaskId,
    actor_id_from_claude_code,
    task_id_from_claude_code,
)
from harness.models.raw_event_builders import CanonicalEventDraft
from harness.models.raw_events import (
    RawEvent,
    TranslationError,
)

if TYPE_CHECKING:
    from domain.event_base import CanonicalEvent, EventPayload
    from harness.impl.claude_code.canonical import records


@dataclass(frozen=True, kw_only=True)
class TaskPayloadSource:
    """Group native fields for one canonical task payload."""

    task_id: ClaudeCodeTaskId | int | None
    subject: str | None
    description: str | None
    state: TaskState
    owner: str | None


def _payload(
    raw_event: RawEvent,
    task_payload_source: TaskPayloadSource,
) -> TaskChanged:
    task_id = task_id_from_claude_code(ClaudeCodeTaskId(str(task_payload_source.task_id or "")))
    if not task_id:
        message = "Claude Code task has no id"
        raise TranslationError(message, context=raw_event.source_position)
    owner_text = str(task_payload_source.owner or "").strip()
    owner_actor_id = actor_id_from_claude_code(ClaudeCodeActorId(owner_text)) if owner_text else raw_event.actor_id
    return TaskChanged(
        task_id,
        str(task_payload_source.subject or ""),
        str(task_payload_source.description or "").strip() or None,
        task_payload_source.state,
        owner_actor_id,
    )


def task_file_event(
    raw_event: RawEvent,
    task: records.TaskFile,
) -> CanonicalEvent[EventPayload]:
    """Return the task file event.

    Returns:
        Task file event.

    Raises:
        TranslationError: If a raw event cannot be translated.

    """
    try:
        state = TaskState(task.status or "")
    except ValueError:
        message = f"unknown Claude Code task state: {task.status!r}"
        raise TranslationError(
            message,
            context=raw_event.source_position,
        ) from None
    payload = _payload(
        raw_event,
        TaskPayloadSource(
            task_id=None if task.id is None else ClaudeCodeTaskId(str(task.id)),
            subject=task.subject,
            description=task.description,
            state=state,
            owner=task.owner,
        ),
    )
    # A task is mutable. Each complete file digest is a separate state fact.
    return event(
        raw_event,
        CanonicalEventDraft(
            "task",
            str(payload.task_id),
            f"changed:{raw_event.source_position}",
            payload,
        ),
    )


def task_hook_event(
    raw_event: RawEvent,
    hook: records.HookPayload,
) -> CanonicalEvent[EventPayload]:
    """Return the task hook event.

    Returns:
        Task hook event.

    Raises:
        TranslationError: If a raw event cannot be translated.

    """
    hook_name = hook.hook_event_name or ""
    if hook_name == "TaskCreated":
        task_state = TaskState.PENDING
    elif hook_name == "TaskCompleted":
        task_state = TaskState.COMPLETED
    else:
        message = f"unknown Claude Code task hook: {hook_name!r}"
        raise TranslationError(message) from None
    payload = _payload(
        raw_event,
        TaskPayloadSource(
            task_id=hook.task_id,
            subject=hook.task_subject,
            description=hook.task_description,
            state=task_state,
            owner=None,
        ),
    )
    return event(raw_event, CanonicalEventDraft("task", str(payload.task_id), f"changed:{hook_name}", payload))
