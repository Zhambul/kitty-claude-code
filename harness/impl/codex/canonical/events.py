
# Copyright (c) 2026 Zhambyl Yermagambet
"""Dispatch declared Codex event payloads."""

from collections.abc import Mapping
from enum import StrEnum
from types import MappingProxyType

from pydantic import BaseModel

from harness.impl.codex.canonical import (
    event_items,
    event_lifecycle,
    event_messages,
)

# Keep event translation separate from foreign payload models.
# isort: split

from harness.impl.codex.canonical import (
    record_event_messages,
    record_goal_payloads,
    record_item_registry,
    record_task_payloads,
    record_terminal_records,
    record_usage_payloads,
)

PHASE_FINAL = "final_answer"


class CodexEventType(StrEnum):
    """Identify one declared Codex event type."""

    USAGE_UPDATED = "token_count"
    THREAD_GOAL_UPDATED = "thread_goal_updated"
    THREAD_GOAL_CLEARED = "thread_goal_cleared"
    CONTEXT_COMPACTED = "context_compacted"
    TASK_STARTED = "task_started"
    TASK_COMPLETE = "task_complete"
    THREAD_SETTINGS_APPLIED = "thread_settings_applied"
    ITEM_COMPLETED = "item_completed"
    TURN_ABORTED = "turn_aborted"
    USER_MESSAGE = "user_message"
    AGENT_REASONING = "agent_reasoning"
    AGENT_MESSAGE = "agent_message"
    WEB_SEARCH_END = "web_search_end"


EVENTS: Mapping[CodexEventType, type[BaseModel]] = MappingProxyType(
    {
        CodexEventType.USAGE_UPDATED: record_usage_payloads.TokenCountPayload,
        CodexEventType.THREAD_GOAL_UPDATED: record_goal_payloads.ThreadGoalUpdatedPayload,
        CodexEventType.THREAD_GOAL_CLEARED: record_goal_payloads.EmptyPayload,
        CodexEventType.CONTEXT_COMPACTED: record_goal_payloads.EmptyPayload,
        CodexEventType.TASK_STARTED: record_task_payloads.TaskStartedPayload,
        CodexEventType.TASK_COMPLETE: record_task_payloads.TaskCompletePayload,
        CodexEventType.THREAD_SETTINGS_APPLIED: record_task_payloads.ThreadSettingsAppliedPayload,
        CodexEventType.ITEM_COMPLETED: record_item_registry.ItemCompletedPayload,
        CodexEventType.TURN_ABORTED: record_event_messages.TurnAbortedPayload,
        CodexEventType.USER_MESSAGE: record_event_messages.UserMessagePayload,
        CodexEventType.AGENT_REASONING: record_event_messages.AgentReasoningPayload,
        CodexEventType.AGENT_MESSAGE: record_event_messages.AgentMessagePayload,
        CodexEventType.WEB_SEARCH_END: record_event_messages.WebSearchEndPayload,
    },
)


def parse_thread_event(payload: BaseModel) -> record_terminal_records.RolloutRecord | None:
    """Parse one thread-level event.

    Returns:
        The thread record, or None for another event group.

    """
    if isinstance(payload, record_usage_payloads.TokenCountPayload):
        return event_lifecycle.token_count(payload)
    if isinstance(payload, record_goal_payloads.ThreadGoalUpdatedPayload):
        return event_lifecycle.goal_updated(payload)
    if isinstance(payload, record_goal_payloads.EmptyPayload):
        return parse_empty_event(payload)
    if isinstance(payload, record_task_payloads.ThreadSettingsAppliedPayload):
        return event_lifecycle.settings_applied(payload)
    return None


def parse_empty_event(payload: record_goal_payloads.EmptyPayload) -> record_terminal_records.RolloutRecord:
    """Parse one event that has no event data.

    Returns:
        The thread record.

    """
    if payload.type == "context_compacted":
        return event_lifecycle.context_compacted(payload)
    return event_lifecycle.goal_cleared(payload)


def parse_task_event(payload: BaseModel) -> record_terminal_records.RolloutRecord | None:
    """Parse one task or completed-item event.

    Returns:
        The task record, or None for another event group.

    """
    if isinstance(payload, record_task_payloads.TaskStartedPayload):
        return event_lifecycle.task_started(payload)
    if isinstance(payload, record_task_payloads.TaskCompletePayload):
        return event_lifecycle.task_complete(payload)
    if isinstance(payload, record_item_registry.ItemCompletedPayload):
        return event_items.item_completed(payload)
    return None


def parse_message_event(payload: BaseModel) -> record_terminal_records.RolloutRecord | None:
    """Parse one message event.

    Returns:
        The message record, or None for another event group.

    """
    if isinstance(payload, record_event_messages.TurnAbortedPayload):
        return event_messages.turn_aborted(payload)
    if isinstance(payload, record_event_messages.UserMessagePayload):
        return event_messages.user_message(payload)
    if isinstance(payload, record_event_messages.AgentReasoningPayload):
        return event_messages.agent_reasoning(payload)
    if isinstance(payload, record_event_messages.AgentMessagePayload):
        return event_messages.agent_message(payload)
    return parse_search_event(payload)


def parse_search_event(payload: BaseModel) -> record_terminal_records.RolloutRecord | None:
    """Parse one search event.

    Returns:
        The search record, or None for another event group.

    """
    if isinstance(payload, record_event_messages.WebSearchEndPayload):
        return event_messages.web_search_end(payload)
    return None


def parse_event(payload: BaseModel) -> record_terminal_records.RolloutRecord | None:
    """Parse one declared Codex event.

    Returns:
        The rollout record, or None if the payload has no canonical fact.

    """
    thread_record = parse_thread_event(payload)
    if thread_record is not None:
        return thread_record
    task_record = parse_task_event(payload)
    if task_record is not None:
        return task_record
    return parse_message_event(payload)
