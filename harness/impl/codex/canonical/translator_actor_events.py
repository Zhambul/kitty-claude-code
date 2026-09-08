# Copyright (c) 2026 Zhambyl Yermagambet
"""Split Codex canonical translation."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harness.impl.codex.canonical import translator_dependencies as dependencies
from harness.impl.codex.canonical.translator_core_values import COMPLETED_STATUS

if TYPE_CHECKING:
    from harness.impl.codex.canonical.translator_state_models import RecordSource


def reasoning_event(
    record_source: RecordSource,
    record: dependencies.record_canonical_namespaces.record_task_records.ReasoningRecord
    | dependencies.record_canonical_namespaces.record_interaction_records.ThinkRecord,
) -> dependencies.translator_type_dependencies.event_base.CanonicalEvent[
    dependencies.translator_type_dependencies.event_base.EventPayload
]:
    """Build a reasoning event from native text.

    Returns:
        The reasoning content with its source identity and time.

    """
    payload = dependencies.translator_domain_events.event_conversation.ReasoningCreated(
        dependencies.translator_id_dependencies.ids_conversation.reasoning_id_from_codex(
            dependencies.translator_id_dependencies.ids_conversation_types.CodexReasoningId(
                record_source.native_identity,
            ),
        ),
        dependencies.translator_codex_dependencies.support.content(record.text, markdown=True),
    )
    return dependencies.translator_codex_dependencies.support.event(
        record_source.raw_event,
        dependencies.translator_service_dependencies.CanonicalEventDraft(
            "reasoning",
            record_source.native_identity,
            "created",
            payload,
            occurred_at=record_source.occurred_at,
        ),
    )


def actor_message_event(
    record_source: RecordSource,
    record: dependencies.record_canonical_namespaces.record_actor_records.ActorActivityRecord,
    call_id: dependencies.translator_id_dependencies.ids_session_types.CodexCallId,
    call_arguments: dependencies.record_payload_namespaces.record_collaboration_arguments.SendMessageArguments,
) -> dependencies.translator_type_dependencies.event_base.CanonicalEvent[
    dependencies.translator_type_dependencies.event_base.EventPayload
]:
    """Build a message event from an actor's send-message call.

    Returns:
        An intermediate assistant message with the receiving actor identifier.

    """
    message_id = dependencies.translator_id_dependencies.ids_conversation.message_id_from_codex_call(call_id)
    spoken = call_arguments.message or call_arguments.content or ""
    payload = dependencies.translator_domain_events.event_conversation.MessageCreated(
        message_id,
        dependencies.translator_domain_values.messaging.MessageRole.ASSISTANT,
        dependencies.translator_codex_dependencies.support.content(spoken, markdown=True),
        dependencies.translator_domain_values.messaging.MessagePhase.INTERMEDIATE,
        None,
        dependencies.translator_id_dependencies.ids_session.actor_id_from_codex(
            dependencies.translator_id_dependencies.ids_session_types.CodexActorId(record.actor_id),
        ),
    )
    return dependencies.translator_codex_dependencies.support.event(
        record_source.raw_event,
        dependencies.translator_service_dependencies.CanonicalEventDraft(
            "message",
            str(message_id),
            "created",
            payload,
            turn_id=dependencies.translator_id_dependencies.ids_conversation.turn_id_from_codex(
                dependencies.translator_id_dependencies.ids_conversation_types.CodexTurnId(record.turn),
            )
            if record.turn
            else None,
            occurred_at=record_source.occurred_at,
        ),
    )


def plan_task_changes(
    record_source: RecordSource,
    record: dependencies.record_canonical_namespaces.record_actor_records.TaskListRecord,
) -> tuple[dependencies.translator_domain_values.event_work.TaskChanged, ...]:
    """Convert native plan tasks to canonical task changes.

    Returns:
        The task changes in native plan order.

    """
    return tuple(
        _plan_task_change(record_source, task_index, plan_task)
        for task_index, plan_task in enumerate(record.tasks, start=1)
    )


def _plan_task_change(
    record_source: RecordSource,
    task_index: int,
    plan_task: dependencies.record_payload_namespaces.record_plan_arguments.PlanTask,
) -> dependencies.translator_domain_values.event_work.TaskChanged:
    subject = (plan_task.step or "").strip()
    if not subject:
        msg = "Codex plan task has no step"
        raise dependencies.translator_service_dependencies.raw_events.TranslationError(msg)
    actor_id = record_source.raw_event.actor_id
    task_id = dependencies.translator_id_dependencies.ids_work.task_id_from_codex(
        dependencies.translator_id_dependencies.ids_work_types.CodexTaskId(f"{actor_id}:plan:{task_index}"),
    )
    return dependencies.translator_domain_values.event_work.TaskChanged(
        task_id,
        subject,
        None,
        _plan_task_state(plan_task),
        record_source.raw_event.actor_id,
    )


def _plan_task_state(
    plan_task: dependencies.record_payload_namespaces.record_plan_arguments.PlanTask,
) -> dependencies.translator_domain_values.work_state.TaskState:
    if plan_task.status == "pending":
        return dependencies.translator_domain_values.work_state.TaskState.PENDING
    if plan_task.status == "in_progress":
        return dependencies.translator_domain_values.work_state.TaskState.IN_PROGRESS
    if plan_task.status == COMPLETED_STATUS:
        return dependencies.translator_domain_values.work_state.TaskState.COMPLETED
    msg = f"unknown Codex plan task state: {plan_task.status!r}"
    raise dependencies.translator_service_dependencies.raw_events.TranslationError(
        msg,
    )


def task_list_event(
    record_source: RecordSource,
    call_id: dependencies.translator_id_dependencies.ids_session_types.CodexCallId,
    current: tuple[dependencies.translator_domain_values.event_work.TaskChanged, ...],
) -> dependencies.translator_type_dependencies.event_base.CanonicalEvent[
    dependencies.translator_type_dependencies.event_base.EventPayload
]:
    """Build the current task list for the source actor.

    Returns:
        A task-list change with the current task identifiers in order.

    """
    return dependencies.translator_codex_dependencies.support.event(
        record_source.raw_event,
        dependencies.translator_service_dependencies.CanonicalEventDraft(
            "task_list",
            str(record_source.raw_event.actor_id),
            f"changed:{call_id}",
            dependencies.translator_domain_values.event_work.TaskListChanged(
                dependencies.translator_id_dependencies.ids_work.task_list_id_from_codex(
                    dependencies.translator_id_dependencies.ids_work_types.CodexTaskListId(
                        str(record_source.raw_event.actor_id),
                    ),
                ),
                tuple(task_changed.task_id for task_changed in current),
            ),
            occurred_at=record_source.occurred_at,
        ),
    )


def changed_task_events(
    record_source: RecordSource,
    call_id: dependencies.translator_id_dependencies.ids_session_types.CodexCallId,
    current: tuple[dependencies.translator_domain_values.event_work.TaskChanged, ...],
    previous: tuple[dependencies.translator_domain_values.event_work.TaskChanged, ...] | None,
) -> list[
    dependencies.translator_type_dependencies.event_base.CanonicalEvent[
        dependencies.translator_type_dependencies.event_base.EventPayload
    ]
]:
    """Build events for tasks that differ from the previous list.

    Returns:
        One event for each new or changed task.

    """
    return [
        dependencies.translator_codex_dependencies.support.event(
            record_source.raw_event,
            dependencies.translator_service_dependencies.CanonicalEventDraft(
                "task",
                str(task_changed.task_id),
                f"changed:{call_id}",
                task_changed,
                occurred_at=record_source.occurred_at,
            ),
        )
        for task_changed in current
        if previous is None or task_changed not in previous
    ]
