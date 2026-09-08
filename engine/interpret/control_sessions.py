# Copyright (c) 2026 Zhambyl Yermagambet
"""Translate session and work-close control effects."""

from domain import (
    event_actor,
    event_conversation,
    event_session,
    event_shell,
    ids,
    outcomes,
    records,
    work_state,
)
from harness.models import control_observations, directives, raw_event_builders, raw_events
from repository.mapper.documents import decode_document


def session_rename(raw_event: raw_events.RawEvent) -> raw_events.TranslationResult:
    """Translate a session rename.

    Returns:
        The translation result.

    """
    observation = decode_document(control_observations.SessionRenameObservation, raw_event.payload)
    return _translation(
        raw_event,
        raw_event_builders.CanonicalEventDraft(
            "session",
            str(raw_event.session_id),
            f"title:{observation.origin}:{raw_event.source_position}",
            event_session.SessionTitleChanged(observation.title, observation.origin),
        ),
    )


def session_close(raw_event: raw_events.RawEvent) -> raw_events.TranslationResult:
    """Translate one open-work item closed with its session.

    Returns:
        The translation result.

    """
    observed = decode_document(control_observations.SessionCloseWorkObservation, raw_event.payload)
    payload: event_conversation.TurnAborted | event_shell.ShellFinished | event_actor.ActorAssignmentFinished
    if observed.kind == work_state.OpenWorkKind.TURN:
        payload = event_conversation.TurnAborted("session closed")
        subject_type = "turn"
        phase = "aborted"
    elif observed.kind == work_state.OpenWorkKind.SHELL:
        payload = event_shell.ShellFinished(
            ids.ShellId(observed.subject_id),
            outcomes.Outcome.CANCELLED,
            None,
            None,
        )
        subject_type = "shell"
        phase = "finished"
    else:
        payload = event_actor.ActorAssignmentFinished(
            ids.AssignmentId(observed.subject_id),
            outcomes.Outcome.CANCELLED,
            None,
            "session closed",
        )
        subject_type = "actor_assignment"
        phase = "finished"
    return _translation(
        raw_event,
        raw_event_builders.CanonicalEventDraft(
            subject_type,
            str(observed.subject_id),
            phase,
            payload,
            turn_id=observed.turn_id,
        ),
    )


def session_finish(raw_event: raw_events.RawEvent) -> raw_events.TranslationResult:
    """Translate a confirmed session close.

    Returns:
        The translation result.

    """
    decode_document(directives.ProcessExit, raw_event.payload)
    finished = event_session.SessionFinished(outcomes.Outcome.UNKNOWN, "session_closed")
    return _translation(
        raw_event,
        raw_event_builders.CanonicalEventDraft(
            "session_control",
            raw_event.source_position,
            "finished",
            finished,
        ),
    )


def _translation(
    raw_event: raw_events.RawEvent,
    draft: raw_event_builders.CanonicalEventDraft,
) -> raw_events.TranslationResult:
    return raw_events.TranslationResult(
        (raw_event_builders.canonical_event(raw_event, draft),),
        records.RecordedTranslationDecision.TRANSLATED,
    )
