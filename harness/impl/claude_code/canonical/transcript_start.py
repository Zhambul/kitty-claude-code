# Copyright (c) 2026 Zhambyl Yermagambet
"""Build canonical events at the start of a Claude transcript."""

from __future__ import annotations

from dataclasses import dataclass

from domain import event_base as domain_event_base, records as domain_records
from harness.impl.claude_code.canonical import messages, records
from harness.models import raw_events


@dataclass(frozen=True)
class TranscriptStart:
    """Contain transcript events that happen before its record."""

    session_events: list[domain_event_base.CanonicalEvent[domain_event_base.EventPayload]]
    metadata_events: list[domain_event_base.CanonicalEvent[domain_event_base.EventPayload]]
    starts_child_actor: bool


def build(
    raw_event: raw_events.RawEvent,
    transcript_document: records.TranscriptDocument,
) -> TranscriptStart:
    """Build the events that start a transcript.

    Returns:
        The events that start a transcript.

    """
    starts_lead_session = (
        raw_event.parent_actor_id is None and bool(transcript_document.cwd) and transcript_document.parent_uuid is None
    )
    starts_child_actor = raw_event.parent_actor_id is not None and raw_event.source_position == "0"
    session_events = (
        messages.session_events(raw_event, transcript_document) if starts_lead_session or starts_child_actor else []
    )
    return TranscriptStart(
        session_events,
        messages.transcript_metadata(raw_event, transcript_document),
        starts_child_actor,
    )


def plumbing_result(transcript_start: TranscriptStart) -> raw_events.TranslationResult:
    """Return the result for a transcript plumbing record.

    Returns:
        The result for a transcript plumbing record.

    """
    events = [*transcript_start.session_events, *transcript_start.metadata_events]
    if events:
        return raw_events.TranslationResult(tuple(events), domain_records.RecordedTranslationDecision.TRANSLATED)
    return raw_events.TranslationResult(
        (),
        domain_records.RecordedTranslationDecision.IGNORED_NONSEMANTIC,
        "transcript plumbing record",
    )
