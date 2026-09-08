# Copyright (c) 2026 Zhambyl Yermagambet
"""Translate Claude Code idle and team messages."""

from harness.impl.claude_code import ids as claude_ids
from harness.impl.claude_code.canonical import (
    message_collaboration_dependencies as dependencies,
    message_models,
    message_subject_values,
    records,
    transcript,
)
from harness.models import raw_events

MISSING_TEAM_MESSAGE_SENDER = "Claude Code teammate message has no sender"


def teammate_idle_events(
    source: message_models.TranscriptSource,
    record: transcript.TeammateIdleTranscriptRecord,
    tool_calls: dependencies.toolcalls.ToolCallSemantics,
) -> list[dependencies.event_base.CanonicalEvent[dependencies.event_base.EventPayload]]:
    """Translate the last idle notification for each teammate.

    Returns:
        Assignment completion events for the applicable actors.

    """
    events: list[dependencies.event_base.CanonicalEvent[dependencies.event_base.EventPayload]] = []
    for resolved_actor_id, actor_notification in _notifications_by_actor(source, record).items():
        events.extend(_idle_actor_events(source, resolved_actor_id, actor_notification, tool_calls))
    return events


def _notifications_by_actor(
    source: message_models.TranscriptSource,
    record: transcript.TeammateIdleTranscriptRecord,
) -> dict[
    dependencies.ids.ActorId,
    tuple[claude_ids.ClaudeCodeActorId, records.TeammateIdleNotificationDocument],
]:
    notifications = {}
    for notification in record.notifications:
        native_actor_id = transcript.teammate_actor_id(
            source.raw_event.source_name,
            notification.from_,
        ) or claude_ids.ClaudeCodeActorId(notification.from_)
        resolved_actor_id = claude_ids.actor_id_from_claude_code(native_actor_id)
        notifications[resolved_actor_id] = (native_actor_id, notification)
    return notifications


def _idle_actor_events(
    source: message_models.TranscriptSource,
    resolved_actor_id: dependencies.ids.ActorId,
    actor_notification: tuple[
        claude_ids.ClaudeCodeActorId,
        records.TeammateIdleNotificationDocument,
    ],
    tool_calls: dependencies.toolcalls.ToolCallSemantics,
) -> list[dependencies.event_base.CanonicalEvent[dependencies.event_base.EventPayload]]:
    native_actor_id, notification = actor_notification
    if source.raw_event.parent_actor_id is not None and resolved_actor_id != source.raw_event.actor_id:
        return []
    assignment_call = tool_calls.assignment_call(
        source.raw_event,
        native_actor_id,
        claude_ids.ClaudeCodeCallId(""),
    )
    if not assignment_call:
        msg = f"Claude Code teammate {notification.from_!r} has no assignment"
        raise raw_events.TranslationError(
            msg,
            context=source.raw_event.source_position,
        )
    tool_calls.assignment_finished(source.raw_event, native_actor_id)
    assignment_id = claude_ids.assignment_id_from_claude_code_call(assignment_call)
    return [
        dependencies.support.event(
            source.raw_event,
            dependencies.raw_event_builders.CanonicalEventDraft(
                "actor_assignment",
                str(assignment_id),
                "finished",
                dependencies.event_actor.ActorAssignmentFinished(
                    assignment_id,
                    _idle_outcome(notification.idle_reason),
                    dependencies.support.content(notification.failure_reason) if notification.failure_reason else None,
                    None,
                ),
                occurred_at=dependencies.support.timestamp(notification.timestamp),
            ),
        ),
    ]


def _idle_outcome(idle_reason: str | None) -> dependencies.outcomes.Outcome:
    if idle_reason == "available":
        return dependencies.outcomes.Outcome.SUCCEEDED
    if idle_reason == "failed":
        return dependencies.outcomes.Outcome.FAILED
    if idle_reason in {"stopped", "cancelled"}:
        return dependencies.outcomes.Outcome.CANCELLED
    return dependencies.outcomes.Outcome.UNKNOWN


def team_message_events(
    source: message_models.TranscriptSource,
    record: transcript.TeamMessageTranscriptRecord,
    *,
    actor_started: bool,
) -> list[dependencies.event_base.CanonicalEvent[dependencies.event_base.EventPayload]]:
    """Translate a team message and start its receiving actor if needed.

    Returns:
        An optional actor start followed by the parent or peer message.

    Raises:
        TranslationError: If the message has no sender.

    """
    if not record.sender:
        raise raw_events.TranslationError(
            MISSING_TEAM_MESSAGE_SENDER,
            context=source.raw_event.source_position,
        )
    is_parent_prompt = record.sender == transcript.LEAD_TEAMMATE_ID and source.raw_event.parent_actor_id is not None
    payload = dependencies.event_conversation.MessageCreated(
        claude_ids.message_id_from_claude_code(
            claude_ids.ClaudeCodeMessageId(source.native_identity),
        ),
        dependencies.messaging.MessageRole.PARENT if is_parent_prompt else dependencies.messaging.MessageRole.PEER,
        dependencies.support.content(record.body),
        dependencies.messaging.MessagePhase.PROMPT if is_parent_prompt else None,
        None,
    )
    events: list[dependencies.event_base.CanonicalEvent[dependencies.event_base.EventPayload]] = []
    if source.raw_event.parent_actor_id is not None and not actor_started:
        actor_draft = dependencies.raw_event_builders.CanonicalEventDraft(
            message_subject_values.ACTOR_SUBJECT,
            str(source.raw_event.actor_id),
            message_subject_values.STARTED_PHASE,
            dependencies.event_actor.ActorStarted(
                str(source.raw_event.actor_id),
                dependencies.messaging.ActorRole.TEAMMATE,
            ),
            occurred_at=None,
        )
        events.append(dependencies.support.event(source.raw_event, actor_draft))
    message_draft = dependencies.raw_event_builders.CanonicalEventDraft(
        message_subject_values.MESSAGE_SUBJECT,
        source.native_identity,
        message_subject_values.CREATED_PHASE,
        payload,
        occurred_at=source.occurred_at,
    )
    events.append(dependencies.support.event(source.raw_event, message_draft))
    return events
