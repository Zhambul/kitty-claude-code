# Copyright (c) 2026 Zhambyl Yermagambet
"""Translate Claude Code assistant content blocks."""

from domain import event_base, event_conversation as conversation_events, messaging
from harness.impl.claude_code import ids as claude_ids
from harness.impl.claude_code.canonical import message_models, message_subject_values, records, support, toolcalls
from harness.models import raw_event_builders


def assistant_block_events(
    source: message_models.TranscriptSource,
    response: message_models.AssistantResponse,
    tool_calls: toolcalls.ToolCallSemantics,
) -> list[event_base.CanonicalEvent[event_base.EventPayload]]:
    """Translate assistant blocks in their original order.

    Returns:
        The canonical events from all supported content blocks.

    """
    events: list[event_base.CanonicalEvent[event_base.EventPayload]] = []
    for block_index, block in enumerate(response.blocks):
        events.extend(assistant_block_event(source, response, tool_calls, block_index, block))
    return events


def assistant_block_event(
    source: message_models.TranscriptSource,
    response: message_models.AssistantResponse,
    tool_calls: toolcalls.ToolCallSemantics,
    block_index: int,
    block: records.MessageContentBlock,
) -> list[event_base.CanonicalEvent[event_base.EventPayload]]:
    """Translate one text, reasoning, or tool-use block.

    Returns:
        The block events, or an empty list for unsupported or empty content.

    """
    block_identity = f"{source.native_identity}:{block_index}"
    if isinstance(block, records.TextBlock) and (block.text or "").strip():
        return [assistant_text_event(source, response, block_index, block_identity, block)]
    if isinstance(block, records.ThinkingBlock) and (block.thinking or "").strip():
        return [assistant_reasoning_event(source, block_identity, block)]
    if isinstance(block, records.ToolUseBlock):
        native_call = records.ToolCallNative(id=block.id, name=block.name, input=block.input)
        return tool_calls.tool_started(source.raw_event, native_call)
    return []


def assistant_text_event(
    source: message_models.TranscriptSource,
    response: message_models.AssistantResponse,
    block_index: int,
    block_identity: str,
    block: records.TextBlock,
) -> event_base.CanonicalEvent[event_base.EventPayload]:
    """Build an assistant message and mark the final text when the turn ends.

    Returns:
        The canonical message event.

    """
    ends_turn = response.ends_turn and block_index == response.last_text_index
    message_id = claude_ids.message_id_from_claude_code(claude_ids.ClaudeCodeMessageId(block_identity))
    payload = conversation_events.MessageCreated(
        message_id,
        messaging.MessageRole.ASSISTANT,
        support.content(block.text, markdown=True),
        messaging.MessagePhase.END_TURN if ends_turn else messaging.MessagePhase.INTERMEDIATE,
        None,
        source.raw_event.parent_actor_id if ends_turn else None,
    )
    draft = raw_event_builders.CanonicalEventDraft(
        message_subject_values.MESSAGE_SUBJECT,
        block_identity,
        message_subject_values.CREATED_PHASE,
        payload,
        occurred_at=source.occurred_at,
    )
    return support.event(source.raw_event, draft)


def assistant_reasoning_event(
    source: message_models.TranscriptSource,
    block_identity: str,
    block: records.ThinkingBlock,
) -> event_base.CanonicalEvent[event_base.EventPayload]:
    """Build a reasoning event from one thinking block.

    Returns:
        The canonical reasoning event.

    """
    reasoning_id = claude_ids.reasoning_id_from_claude_code(claude_ids.ClaudeCodeReasoningId(block_identity))
    payload = conversation_events.ReasoningCreated(
        reasoning_id,
        support.content(block.thinking, markdown=True),
    )
    draft = raw_event_builders.CanonicalEventDraft(
        "reasoning",
        block_identity,
        message_subject_values.CREATED_PHASE,
        payload,
        occurred_at=source.occurred_at,
    )
    return support.event(source.raw_event, draft)
