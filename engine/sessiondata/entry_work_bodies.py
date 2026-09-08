# Copyright (c) 2026 Zhambyl Yermagambet
"""Create feed bodies for work events."""

from __future__ import annotations

from typing import TYPE_CHECKING

from domain import (
    entry_attention,
    entry_base,
    entry_lifecycle,
    event_actor,
    event_resource,
    event_telemetry,
    event_work,
    outcomes,
)

if TYPE_CHECKING:
    from domain import event_base


def work_body(event_payload: event_base.EventPayload) -> entry_base.EntryBody | None:
    """Return the work-event body.

    Returns:
        The entry body, or none when no work body applies.

    """
    for body in (skill_body(event_payload), attention_body(event_payload), lifecycle_body(event_payload)):
        if body is not None:
            return body
    return None


def skill_body(event_payload: event_base.EventPayload) -> entry_base.EntryBody | None:
    """Return the skill body.

    Returns:
        The entry body, or none when the event is not a skill event.

    """
    if isinstance(event_payload, event_resource.SkillStarted):
        return entry_attention.SkillStartedBody(event_payload.skill_id, event_payload.name, event_payload.arguments)
    if isinstance(event_payload, event_resource.SkillFinished):
        return entry_attention.SkillFinishedBody(
            event_payload.skill_id,
            run_state(event_payload.outcome),
            event_payload.result,
        )
    return None


def attention_body(event_payload: event_base.EventPayload) -> entry_base.EntryBody | None:
    """Return the attention body.

    Returns:
        The entry body, or none when the event is not an attention event.

    """
    if isinstance(event_payload, event_work.QuestionAsked):
        return entry_attention.QuestionAskedBody(event_payload.attention_id, event_payload.questions)
    if isinstance(event_payload, event_work.QuestionAnswered):
        return entry_attention.QuestionAnsweredBody(
            event_payload.attention_id,
            event_payload.answers,
            event_payload.feedback,
        )
    if isinstance(event_payload, event_work.PlanProposed):
        return entry_attention.PlanProposedBody(event_payload.attention_id, event_payload.plan)
    if isinstance(event_payload, event_work.PlanResolved):
        return entry_attention.PlanResolvedBody(
            event_payload.attention_id,
            event_payload.state,
            event_payload.feedback,
            event_payload.edited,
        )
    return None


def lifecycle_body(event_payload: event_base.EventPayload) -> entry_base.EntryBody | None:
    """Return the lifecycle work body.

    Returns:
        The entry body, or none when no lifecycle event applies.

    """
    if isinstance(event_payload, event_telemetry.CompactionStarted):
        return entry_lifecycle.CompactionStartedBody(event_payload.before_tokens)
    if isinstance(event_payload, event_telemetry.CompactionFinished):
        return entry_lifecycle.CompactionFinishedBody(
            event_payload.before_tokens,
            event_payload.after_tokens,
            event_payload.context,
        )
    if isinstance(event_payload, event_actor.ActorAssignmentStarted):
        return entry_lifecycle.AssignmentStartedBody(
            event_payload.assignment_id,
            event_payload.actor_name,
            event_payload.prompt,
        )
    if isinstance(event_payload, event_actor.ActorAssignmentFinished):
        return entry_lifecycle.AssignmentFinishedBody(
            event_payload.assignment_id,
            run_state(event_payload.outcome),
            event_payload.result,
        )
    return None


def run_state(outcome: outcomes.Outcome) -> entry_base.RunState:
    """Return the run state.

    Returns:
        The run state.

    """
    if outcome == outcomes.Outcome.CANCELLED:
        return entry_base.RunState.CANCELLED
    return entry_base.RunState.SUCCEEDED if outcome == outcomes.Outcome.SUCCEEDED else entry_base.RunState.FAILED
