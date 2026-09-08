
# Copyright (c) 2026 Zhambyl Yermagambet
"""Convert Codex message events."""

from harness.impl.codex.canonical import (
    record_event_messages,
    record_task_records,
    record_terminal_records,
    record_tool_records,
)
from harness.impl.codex.canonical.vocabulary import empty_record, strip_input_wrapper


def turn_aborted(payload: record_event_messages.TurnAbortedPayload) -> record_task_records.TurnAbortedRecord:
    """Convert one aborted turn.

    Returns:
        The aborted turn record.

    """
    return record_task_records.TurnAbortedRecord(turn=payload.turn_id or "")


def user_message(payload: record_event_messages.UserMessagePayload) -> record_terminal_records.RolloutRecord:
    """Convert one user message.

    Returns:
        The prompt record or an empty record.

    """
    message = strip_input_wrapper((payload.message or "").strip())
    return record_task_records.PromptRecord(text=message) if message else empty_record()


def agent_reasoning(payload: record_event_messages.AgentReasoningPayload) -> record_terminal_records.RolloutRecord:
    """Convert one reasoning message.

    Returns:
        The reasoning record or an empty record.

    """
    reasoning_text = (payload.text or "").strip()
    return record_task_records.ReasoningRecord(text=reasoning_text) if reasoning_text else empty_record()


def agent_message(payload: record_event_messages.AgentMessagePayload) -> record_terminal_records.RolloutRecord:
    """Convert one agent message.

    Returns:
        The message record or an empty record.

    """
    message = (payload.message or "").strip()
    phase = (payload.phase or "").strip()
    return record_task_records.MessageRecord(text=message, phase=phase) if message else empty_record()


def web_search_end(payload: record_event_messages.WebSearchEndPayload) -> record_tool_records.SearchRecord | None:
    """Convert one completed web search.

    Returns:
        The search record, or None if the event has no query.

    """
    query = (payload.query or "").strip()
    if not query and payload.action is not None:
        query = (payload.action.query or "").strip()
    return record_tool_records.SearchRecord(query=query) if query else None
