# Copyright (c) 2026 Zhambyl Yermagambet
"""Dispatch Claude Code transcript translation."""

from domain import event_base
from harness.impl.claude_code.canonical import message_models, records, transcript
from harness.impl.claude_code.canonical.message_collaboration_dispatch import translate_collaboration_record
from harness.impl.claude_code.canonical.message_conversation_dispatch import translate_conversation_record
from harness.impl.claude_code.canonical.message_direct_dispatch import translate_direct_record
from harness.impl.claude_code.canonical.message_source import transcript_source
from harness.models import raw_events


def translate_transcript(
    raw_event: raw_events.RawEvent,
    transcript_document: records.TranscriptDocument,
    record: transcript.TranscriptRecord,
    semantics: message_models.TranscriptSemantics,
) -> list[event_base.CanonicalEvent[event_base.EventPayload]]:
    """Translate a transcript record.

    Returns:
        The canonical events.

    """
    source = transcript_source(raw_event, transcript_document)
    translated = translate_direct_record(source, record, semantics)
    if translated is not None:
        return translated
    translated = translate_collaboration_record(source, record, semantics)
    if translated is not None:
        return translated
    return translate_conversation_record(source, record, semantics)
