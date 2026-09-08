# Copyright (c) 2026 Zhambyl Yermagambet
"""Translate Claude Code session records."""

from harness.impl.claude_code.canonical import message_session_dependencies as dependencies, records
from harness.impl.claude_code.canonical.message_child_session import child_session_events
from harness.impl.claude_code.canonical.message_lead_session import lead_session_events
from harness.models import raw_events


def transcript_metadata(
    raw_event: raw_events.RawEvent,
    transcript_document: records.TranscriptDocument,
) -> list[dependencies.event_base.CanonicalEvent[dependencies.event_base.EventPayload]]:
    """Translate transcript title metadata.

    Returns:
        The title events.

    """
    if raw_event.parent_actor_id is not None:
        return []
    record_type = transcript_document.type
    if record_type not in {"agent-name", "ai-title", "summary"}:
        return []
    if record_type == "agent-name":
        title = str(transcript_document.agent_name or "").strip()
        origin = dependencies.work_state.TitleOrigin.CUSTOM
    elif record_type == "ai-title":
        title = str(transcript_document.ai_title or "").strip()
        origin = dependencies.work_state.TitleOrigin.AUTOMATIC
    else:
        title = str(transcript_document.summary or "").strip()
        origin = dependencies.work_state.TitleOrigin.SUMMARY
    if not title:
        return []
    draft = dependencies.raw_event_builders.CanonicalEventDraft(
        "session",
        str(raw_event.session_id),
        f"title:{origin}:{raw_event.source_position}",
        dependencies.event_session.SessionTitleChanged(title, origin),
    )
    return [dependencies.support.event(raw_event, draft)]


def session_events(
    raw_event: raw_events.RawEvent,
    document: records.TranscriptDocument | records.HookPayload,
) -> list[dependencies.event_base.CanonicalEvent[dependencies.event_base.EventPayload]]:
    """Translate session start records.

    Returns:
        The session events.

    """
    if raw_event.parent_actor_id is not None:
        return child_session_events(raw_event)
    return lead_session_events(raw_event, document)
