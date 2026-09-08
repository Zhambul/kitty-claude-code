
# Copyright (c) 2026 Zhambyl Yermagambet
"""Convert Codex lifecycle events."""

from harness.impl.codex.canonical import (
    record_actor_records,
    record_context_records,
    record_goal_payloads,
    record_interaction_records,
    record_task_payloads,
    record_task_records,
    record_terminal_records,
    record_usage_payloads,
)
from harness.impl.codex.canonical.vocabulary import empty_record


def token_count(payload: record_usage_payloads.TokenCountPayload) -> record_terminal_records.RolloutRecord:
    """Convert one cumulative token snapshot.

    Returns:
        The usage record or an empty record.

    """
    if payload.usage_info is None or payload.usage_info.total_token_usage is None:
        return empty_record()
    return record_context_records.UsageRecord(
        usage=payload.usage_info.total_token_usage,
        last=payload.usage_info.last_token_usage,
        window=payload.usage_info.model_context_window,
    )


def goal_updated(payload: record_goal_payloads.ThreadGoalUpdatedPayload) -> record_actor_records.GoalRecord | None:
    """Convert one goal update.

    Returns:
        The goal record, or None if no goal is present.

    """
    if payload.goal is None:
        return None
    goal = payload.goal
    return record_actor_records.GoalRecord(objective=goal.objective, status=goal.status, reason=goal.reason)


def goal_cleared(_payload: record_goal_payloads.EmptyPayload) -> record_actor_records.GoalRecord:
    """Return a cleared goal record.

    Returns:
        The cleared goal record.

    """
    return record_actor_records.GoalRecord(objective=None, status="cleared", reason=None)


def context_compacted(_payload: record_goal_payloads.EmptyPayload) -> record_context_records.CompactRecord:
    """Return a completed compaction record.

    Returns:
        The completed compaction record.

    """
    return record_context_records.CompactRecord()


def task_started(payload: record_task_payloads.TaskStartedPayload) -> record_task_records.TaskStartedRecord:
    """Convert one task start.

    Returns:
        The task start record.

    """
    return record_task_records.TaskStartedRecord(at=payload.started_at, turn=payload.turn_id or "")


def task_complete(payload: record_task_payloads.TaskCompletePayload) -> record_task_records.TaskCompleteRecord:
    """Convert one task completion.

    Returns:
        The task completion record.

    """
    return record_task_records.TaskCompleteRecord(
        at=payload.completed_at,
        turn=payload.turn_id or "",
        last=(payload.last_agent_message or "").strip(),
    )


def settings_applied(
    payload: record_task_payloads.ThreadSettingsAppliedPayload,
) -> record_interaction_records.SettingsRecord:
    """Convert the current model picker settings.

    Returns:
        The current model and effort settings.

    """
    settings = payload.thread_settings
    return record_interaction_records.SettingsRecord(
        model=settings.model if settings else None,
        effort=settings.reasoning_effort if settings else None,
    )
