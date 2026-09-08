# Copyright (c) 2026 Zhambyl Yermagambet
"""Translate Claude Code lead session records."""

from harness.impl.claude_code.canonical import (
    message_session_dependencies as dependencies,
    message_subject_values as subject_values,
    records,
)
from harness.models import raw_events


def lead_session_events(
    raw_event: raw_events.RawEvent,
    document: records.TranscriptDocument | records.HookPayload,
) -> list[dependencies.event_base.CanonicalEvent[dependencies.event_base.EventPayload]]:
    """Build the initial lead session and actor events.

    Returns:
        The session and actor start events, with run and account events when available.

    """
    session_started = _session_started(raw_event, document)
    actor_started = dependencies.event_actor.ActorStarted("claude", dependencies.messaging.ActorRole.LEAD)
    events = _lead_start_events(raw_event, session_started, actor_started)
    account_event = _session_account_event(raw_event)
    if account_event is not None:
        events.append(account_event)
    return events


def _session_started(
    raw_event: raw_events.RawEvent,
    document: records.TranscriptDocument | records.HookPayload,
) -> dependencies.event_session.SessionStarted:
    transcript_path = str(document.transcript_path or "")
    source_reference = dependencies.os.path.realpath(transcript_path) if transcript_path else raw_event.source_name
    return dependencies.event_session.SessionStarted(
        working_directory=str(document.cwd or ""),
        source_reference=source_reference,
        resumed_from=None,
        title=None,
        model=None,
        effort=None,
        account=None,
    )


def _lead_start_events(
    raw_event: raw_events.RawEvent,
    session_started: dependencies.event_session.SessionStarted,
    actor_started: dependencies.event_actor.ActorStarted,
) -> list[dependencies.event_base.CanonicalEvent[dependencies.event_base.EventPayload]]:
    if raw_event.source_type == "hook" and raw_event.terminal_window_id is not None:
        return list(
            dependencies.raw_event_builders.session_run_started_events(
                raw_event,
                session_started,
                actor_started,
            ),
        )
    session_draft = dependencies.raw_event_builders.CanonicalEventDraft(
        "session",
        str(raw_event.session_id),
        subject_values.STARTED_PHASE,
        session_started,
    )
    actor_draft = dependencies.raw_event_builders.CanonicalEventDraft(
        subject_values.ACTOR_SUBJECT,
        str(raw_event.actor_id),
        subject_values.STARTED_PHASE,
        actor_started,
    )
    return [
        dependencies.support.event(raw_event, session_draft),
        dependencies.support.event(raw_event, actor_draft),
    ]


def _session_account_event(
    raw_event: raw_events.RawEvent,
) -> dependencies.event_base.CanonicalEvent[dependencies.event_base.EventPayload] | None:
    if raw_event.account_id is None and raw_event.account_display_name is None:
        return None
    account_id = raw_event.account_id or dependencies.ids.AccountId("")
    display_name = raw_event.account_display_name or account_id or "default"
    payload = dependencies.event_session.SessionAccountChanged(
        dependencies.references.AccountReference(account_id, display_name),
    )
    draft = dependencies.raw_event_builders.CanonicalEventDraft(
        "session",
        str(raw_event.session_id),
        f"account:{raw_event.source_position}",
        payload,
    )
    return dependencies.support.event(raw_event, draft)
