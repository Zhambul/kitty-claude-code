# Copyright (c) 2026 Zhambyl Yermagambet
"""Dispatch Claude Code conversation records."""

from domain import event_base
from harness.impl.claude_code.canonical import message_models, transcript
from harness.impl.claude_code.canonical.message_assistant_blocks import assistant_block_events
from harness.impl.claude_code.canonical.message_assistant_metrics import (
    assistant_model_events,
    assistant_turn_events,
    assistant_usage_events,
)
from harness.impl.claude_code.canonical.message_assistant_response import assistant_response
from harness.impl.claude_code.canonical.message_markers import compaction_event, recap_event
from harness.impl.claude_code.canonical.message_result_state import results_events


def translate_conversation_record(
    source: message_models.TranscriptSource,
    record: transcript.TranscriptRecord,
    semantics: message_models.TranscriptSemantics,
) -> list[event_base.CanonicalEvent[event_base.EventPayload]]:
    """Translate assistant responses, tool results, and conversation markers.

    Returns:
        The ordered events for the record, or no events for an unsupported record.

    """
    if isinstance(record, transcript.AssistantTranscriptRecord):
        response = assistant_response(record)
        events = assistant_block_events(source, response, semantics.tool_calls)
        events.extend(assistant_model_events(source, response, semantics.selections))
        events.extend(assistant_usage_events(source, response))
        events.extend(assistant_turn_events(source, response, semantics))
        return events
    if isinstance(record, transcript.ResultsTranscriptRecord):
        return results_events(source, record, semantics)
    return translate_conversation_marker(source, record)


def translate_conversation_marker(
    source: message_models.TranscriptSource,
    record: transcript.TranscriptRecord,
) -> list[event_base.CanonicalEvent[event_base.EventPayload]]:
    """Translate a compaction summary or recap marker.

    Returns:
        The summary event, or no events for other markers.

    """
    if isinstance(record, transcript.CompactTranscriptRecord):
        return []
    if isinstance(record, transcript.CompactSummaryTranscriptRecord):
        return [compaction_event(source, record)]
    if isinstance(record, transcript.TextTranscriptRecord) and record.kind == transcript.TranscriptKind.RECAP:
        return [recap_event(source, record)]
    return []
