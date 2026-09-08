# Copyright (c) 2026 Zhambyl Yermagambet
"""Build Claude Code prompt events."""

from domain import event_base, event_conversation as conversation_events, messaging
from harness.impl.claude_code.canonical import (
    message_models,
    message_prompt_dependencies as dependencies,
    message_subject_values as subject_values,
    transcript,
)
from harness.impl.claude_code.canonical.message_skills import _loaded_skill
from harness.models import raw_events


def prompt_skill_event(
    raw_event: raw_events.RawEvent,
    record: transcript.PromptTranscriptRecord,
    tool_calls: dependencies.toolcalls.ToolCallSemantics,
) -> event_base.CanonicalEvent[event_base.EventPayload] | None:
    """Read a skill load result from a synthetic prompt.

    Returns:
        The skill event, or None if no matching skill load is found.

    """
    if not record.meta:
        return None
    loaded_skill = _loaded_skill(record.text)
    if loaded_skill is None:
        return None
    name, output = loaded_skill
    return tool_calls.skill_loaded(raw_event, name, output)


def prompt_message(
    source: message_models.TranscriptSource,
    record: transcript.PromptTranscriptRecord,
    turn_semantics: dependencies.turns.TurnSemantics,
) -> message_models.PromptMessage:
    """Build a prompt message with its role and interruption state.

    Returns:
        The prompt message and its associated turn information.

    """
    role = prompt_role(source.raw_event, synthetic=record.meta)
    interruption = prompt_interruption(source.raw_event, record, role, turn_semantics)
    message_id = dependencies.ids.message_id_from_claude_code(
        dependencies.ids.ClaudeCodeMessageId(source.native_identity),
    )
    payload = conversation_events.MessageCreated(
        message_id,
        role,
        dependencies.support.content(record.text),
        messaging.MessagePhase.SYNTHETIC if record.meta else messaging.MessagePhase.PROMPT,
        None,
    )
    draft = dependencies.raw_event_builders.CanonicalEventDraft(
        subject_values.MESSAGE_SUBJECT,
        source.native_identity,
        subject_values.CREATED_PHASE,
        payload,
        turn_id=interruption.turn_id if record.interrupted else None,
        occurred_at=source.occurred_at,
    )
    return message_models.PromptMessage(
        role,
        interruption,
        dependencies.support.event(source.raw_event, draft),
    )


def prompt_role(raw_event: raw_events.RawEvent, *, synthetic: bool) -> messaging.MessageRole:
    """Select the role for a prompt source.

    Returns:
        System for synthetic text, parent for child actors, or user for lead actors.

    """
    if synthetic:
        return messaging.MessageRole.SYSTEM
    if raw_event.parent_actor_id is not None:
        return messaging.MessageRole.PARENT
    return messaging.MessageRole.USER


def prompt_interruption(
    raw_event: raw_events.RawEvent,
    record: transcript.PromptTranscriptRecord,
    role: messaging.MessageRole,
    turn_semantics: dependencies.turns.TurnSemantics,
) -> message_models.PromptInterruption:
    """Record interruption or replacement of a turn by a queued user prompt.

    Returns:
        The affected turn and whether its abort event was already emitted.

    """
    if record.interrupted:
        turn_id, abort_already_emitted = turn_semantics.interrupted(raw_event)
        return message_models.PromptInterruption(turn_id, abort_already_emitted)
    if record.queued and role == messaging.MessageRole.USER:
        return message_models.PromptInterruption(
            turn_semantics.replace_for_queued_prompt(raw_event), abort_already_emitted=False,
        )
    return message_models.PromptInterruption(None, abort_already_emitted=False)
