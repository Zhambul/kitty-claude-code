# Copyright (c) 2026 Zhambyl Yermagambet
"""Dispatch Claude Code prompt translation."""

from domain import event_base, messaging
from harness.impl.claude_code.canonical import (
    message_models,
    message_prompt_building as building,
    message_prompt_outcomes as outcomes,
    transcript,
)


def translate_prompt(
    source: message_models.TranscriptSource,
    record: transcript.PromptTranscriptRecord,
    semantics: message_models.TranscriptSemantics,
) -> list[event_base.CanonicalEvent[event_base.EventPayload]]:
    """Translate a prompt record.

    Returns:
        The prompt events.

    """
    skill_event = building.prompt_skill_event(source.raw_event, record, semantics.tool_calls)
    if skill_event is not None:
        return [skill_event]
    prompt_message = building.prompt_message(source, record, semantics.turns)
    if record.interrupted:
        return outcomes.interrupted_prompt_events(source, prompt_message)
    if record.resumed:
        return outcomes.resumed_prompt_events(source, prompt_message, semantics.turns)
    if prompt_message.role != messaging.MessageRole.USER:
        return [prompt_message.created]
    return outcomes.user_prompt_events(source, prompt_message, semantics.turns)
