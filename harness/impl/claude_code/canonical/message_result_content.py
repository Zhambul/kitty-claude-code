# Copyright (c) 2026 Zhambyl Yermagambet
"""Translate Claude Code result content."""

from harness.impl.claude_code import ids as claude_ids
from harness.impl.claude_code.canonical import (
    message_models,
    message_result_dependencies as dependencies,
    message_subject_values as subject_values,
    records,
    toolcalls,
    transcript,
)
from harness.impl.claude_code.canonical.message_result_models import ResultInterruption


def tool_result_events(
    source: message_models.TranscriptSource,
    record: transcript.ResultsTranscriptRecord,
    tool_calls: toolcalls.ToolCallSemantics,
) -> list[dependencies.event_base.CanonicalEvent[dependencies.event_base.EventPayload]]:
    """Translate each tool result block in a transcript record.

    Returns:
        Tool result events in block order.

    """
    events: list[dependencies.event_base.CanonicalEvent[dependencies.event_base.EventPayload]] = []
    sidecar = record.tool_response if len(record.blocks) == 1 else None
    for tool_result_block in record.blocks:
        events.extend(tool_result_block_events(source, record, tool_result_block, sidecar, tool_calls))
    return events


def tool_result_block_events(
    source: message_models.TranscriptSource,
    record: transcript.ResultsTranscriptRecord,
    tool_result_block: records.ToolResultBlock,
    sidecar: records.ToolResponse | records.ToolResponseBlocks | str | None,
    tool_calls: toolcalls.ToolCallSemantics,
) -> list[dependencies.event_base.CanonicalEvent[dependencies.event_base.EventPayload]]:
    """Translate a tool result and update its tracked call state.

    Returns:
        Result and declined-attention events, or no events for a background launch placeholder.

    """
    call_id = claude_ids.ClaudeCodeCallId(tool_result_block.tool_use_id or source.native_identity)
    result_text = transcript.result_text(tool_result_block.content)
    if result_text.startswith(toolcalls.BACKGROUND_LAUNCH_STUB):
        tool_calls.forget(source.raw_event, call_id)
        return []
    failed = bool(tool_result_block.is_error)
    events = tool_calls.tool_result(
        source.raw_event,
        toolcalls.TranscriptToolResult(call_id, result_text, sidecar, failed, record.cancelled),
    )
    if failed and tool_calls.pending_attention(source.raw_event, call_id):
        events.append(tool_calls.attention_declined(source.raw_event, call_id, result_text))
    if not tool_calls.is_skill(source.raw_event, call_id):
        tool_calls.forget(source.raw_event, call_id)
    return events


def result_text_events(
    source: message_models.TranscriptSource,
    record: transcript.ResultsTranscriptRecord,
    loaded_skill_texts: set[int],
    turn_id: dependencies.ids.TurnId | None,
) -> list[dependencies.event_base.CanonicalEvent[dependencies.event_base.EventPayload]]:
    """Translate result texts that were not consumed as skill loads.

    Returns:
        Message events in the original text order.

    """
    events: list[dependencies.event_base.CanonicalEvent[dependencies.event_base.EventPayload]] = []
    for text_index, result_text in enumerate(record.texts):
        if text_index not in loaded_skill_texts:
            events.append(result_text_event(source, record, text_index, result_text, turn_id))
    return events


def result_text_event(
    source: message_models.TranscriptSource,
    record: transcript.ResultsTranscriptRecord,
    text_index: int,
    result_text: str,
    turn_id: dependencies.ids.TurnId | None,
) -> dependencies.event_base.CanonicalEvent[dependencies.event_base.EventPayload]:
    """Build a message for one result text.

    Returns:
        A synthetic system message or user prompt with the supplied turn identifier.

    """
    text_identity = f"{source.native_identity}:text:{text_index}"
    message_id = claude_ids.message_id_from_claude_code(
        claude_ids.ClaudeCodeMessageId(text_identity),
    )
    payload = dependencies.event_conversation.MessageCreated(
        message_id,
        dependencies.messaging.MessageRole.SYSTEM if record.meta else dependencies.messaging.MessageRole.USER,
        dependencies.support.content(result_text),
        dependencies.messaging.MessagePhase.SYNTHETIC if record.meta else dependencies.messaging.MessagePhase.PROMPT,
        None,
    )
    draft = dependencies.raw_event_builders.CanonicalEventDraft(
        subject_values.MESSAGE_SUBJECT,
        text_identity,
        subject_values.CREATED_PHASE,
        payload,
        turn_id=turn_id,
    )
    return dependencies.support.event(source.raw_event, draft)


def finalize_result_interruption(
    source: message_models.TranscriptSource,
    record: transcript.ResultsTranscriptRecord,
    result_interruption: ResultInterruption,
    events: list[dependencies.event_base.CanonicalEvent[dependencies.event_base.EventPayload]],
) -> list[dependencies.event_base.CanonicalEvent[dependencies.event_base.EventPayload]]:
    """Attach interruption state to the translated result events.

    Returns:
        Events with missing turn identifiers filled in and any required abort appended.

    """
    if record.interrupted and result_interruption.turn_id is not None:
        events = [
            dependencies.replace(canonical_record, turn_id=result_interruption.turn_id)
            if canonical_record.turn_id is None
            else canonical_record
            for canonical_record in events
        ]
    if record.interrupted and not result_interruption.abort_already_emitted:
        draft = dependencies.raw_event_builders.CanonicalEventDraft(
            subject_values.TURN_SUBJECT,
            str(result_interruption.turn_id) if result_interruption.turn_id else source.native_identity,
            "aborted",
            dependencies.event_conversation.TurnAborted(None),
            turn_id=result_interruption.turn_id,
            occurred_at=source.occurred_at,
        )
        events.append(dependencies.support.event(source.raw_event, draft))
    return events
