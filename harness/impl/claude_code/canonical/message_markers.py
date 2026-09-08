# Copyright (c) 2026 Zhambyl Yermagambet
"""Translate Claude Code compaction and recap markers."""

from domain import event_base, event_conversation as conversation_events, event_telemetry, messaging
from harness.impl.claude_code import ids as claude_ids
from harness.impl.claude_code.canonical import message_models, message_subject_values, support, transcript
from harness.models import raw_event_builders


def compaction_event(
    source: message_models.TranscriptSource,
    record: transcript.CompactSummaryTranscriptRecord,
) -> event_base.CanonicalEvent[event_base.EventPayload]:
    """Translate a completed compaction summary.

    Returns:
        The compaction event with its summary and prior token count.

    """
    payload = event_telemetry.CompactionFinished(
        record.before_tokens,
        None,
        support.content(record.text, markdown=True),
    )
    draft = raw_event_builders.CanonicalEventDraft(
        "compaction",
        record.boundary_id or source.native_identity,
        "finished",
        payload,
        occurred_at=source.occurred_at,
    )
    return support.event(source.raw_event, draft)


def recap_event(
    source: message_models.TranscriptSource,
    record: transcript.TextTranscriptRecord,
) -> event_base.CanonicalEvent[event_base.EventPayload]:
    """Translate a recap into a system message.

    Returns:
        The canonical recap message event.

    """
    message_id = claude_ids.message_id_from_claude_code(
        claude_ids.ClaudeCodeMessageId(source.native_identity),
    )
    payload = conversation_events.MessageCreated(
        message_id,
        messaging.MessageRole.SYSTEM,
        support.content(record.text, markdown=True),
        messaging.MessagePhase.RECAP,
        None,
    )
    draft = raw_event_builders.CanonicalEventDraft(
        message_subject_values.MESSAGE_SUBJECT,
        source.native_identity,
        message_subject_values.CREATED_PHASE,
        payload,
        occurred_at=source.occurred_at,
    )
    return support.event(source.raw_event, draft)
