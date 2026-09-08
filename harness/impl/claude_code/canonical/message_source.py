# Copyright (c) 2026 Zhambyl Yermagambet
"""Build a Claude Code transcript translation source."""

from harness.impl.claude_code.canonical import records
from harness.impl.claude_code.canonical.message_models import TranscriptSource
from harness.impl.claude_code.canonical.support import timestamp
from harness.models import raw_events


def transcript_source(
    raw_event: raw_events.RawEvent,
    transcript_document: records.TranscriptDocument,
) -> TranscriptSource:
    """Build source metadata for transcript translation.

    Returns:
        The raw event and document with a native identity and parsed timestamp.

    """
    message_id = None if transcript_document.message is None else transcript_document.message.id
    native_identity = str(transcript_document.uuid or message_id or raw_event.source_position)
    return TranscriptSource(
        raw_event,
        transcript_document,
        native_identity,
        timestamp(transcript_document.timestamp),
    )
