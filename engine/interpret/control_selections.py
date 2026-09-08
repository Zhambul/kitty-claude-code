# Copyright (c) 2026 Zhambyl Yermagambet
"""Translate selection and message control effects."""

from domain import (
    content,
    event_conversation,
    event_session,
    event_work,
    records,
    references,
    work_state,
)
from harness.models import control_observations, raw_event_builders, raw_events
from repository.mapper.documents import decode_document


def model_selection(raw_event: raw_events.RawEvent) -> raw_events.TranslationResult:
    """Translate a model selection.

    Returns:
        The translation result.

    """
    observation = decode_document(control_observations.ModelSelectionObservation, raw_event.payload)
    changed = event_session.ModelChanged(
        None,
        references.ModelReference(observation.model, observation.model),
        work_state.ModelChangeReason.SELECTED,
    )
    return _translation(
        raw_event,
        raw_event_builders.CanonicalEventDraft(
            "model",
            str(raw_event.actor_id),
            f"selected:{raw_event.source_position}",
            changed,
        ),
    )


def effort_selection(raw_event: raw_events.RawEvent) -> raw_events.TranslationResult:
    """Translate an effort selection.

    Returns:
        The translation result.

    """
    observation = decode_document(control_observations.EffortSelectionObservation, raw_event.payload)
    changed = event_session.EffortChanged(
        None,
        observation.effort,
        work_state.EffortChangeReason.SELECTED,
    )
    return _translation(
        raw_event,
        raw_event_builders.CanonicalEventDraft(
            "effort",
            str(raw_event.actor_id),
            f"selected:{raw_event.source_position}",
            changed,
        ),
    )


def message_queued(raw_event: raw_events.RawEvent) -> raw_events.TranslationResult:
    """Translate a queued message.

    Returns:
        The translation result.

    """
    observation = decode_document(control_observations.MessageQueueObservation, raw_event.payload)
    queued = event_conversation.MessageQueued(
        observation.request_id,
        content.TextContent(observation.text),
    )
    return _translation(
        raw_event,
        raw_event_builders.CanonicalEventDraft(
            "message_queue",
            str(observation.request_id),
            "queued",
            queued,
        ),
    )


def plan_decision(raw_event: raw_events.RawEvent) -> raw_events.TranslationResult:
    """Translate a plan decision.

    Returns:
        The translation result.

    """
    observation = decode_document(control_observations.PlanDecisionObservation, raw_event.payload)
    resolved = event_work.PlanResolved(
        observation.attention_id,
        observation.state,
        observation.feedback,
        observation.edited,
    )
    return _translation(
        raw_event,
        raw_event_builders.CanonicalEventDraft(
            "plan",
            str(observation.attention_id),
            raw_event_builders.plan_resolution_phase(resolved),
            resolved,
            turn_id=observation.turn_id,
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
