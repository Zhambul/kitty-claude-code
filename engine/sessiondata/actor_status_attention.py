# Copyright (c) 2026 Zhambyl Yermagambet
"""Actor status attention."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from domain import (
    actor_state,
    event_actor,
    event_shell,
    event_work,
)

if TYPE_CHECKING:
    from domain import event_base, ids
    from engine.sessiondata import contract

from engine.sessiondata.actor_status_background import _added, _without_background
from engine.sessiondata.actor_status_work import _status_after_work_settled


def _assignment_status(
    aggregate_state: contract.AggregateState,
    event: event_base.CanonicalEvent[event_base.EventPayload],
    actor: actor_state.ActorFacts,
    payload: event_base.EventPayload,
) -> contract.AggregateState | None:
    if isinstance(payload, event_actor.ActorAssignmentStarted):
        return _start_assignment(aggregate_state, event, actor, payload)
    if isinstance(payload, event_actor.ActorAssignmentFinished):
        return _finish_assignment(aggregate_state, actor, payload)
    return None


def _attention_status(
    aggregate_state: contract.AggregateState,
    actor: actor_state.ActorFacts,
    payload: event_base.EventPayload,
) -> contract.AggregateState | None:
    if isinstance(payload, event_shell.ShellOutputFinished):
        return _finish_shell_output(aggregate_state, actor, payload)
    if isinstance(payload, (event_work.QuestionAsked, event_work.PlanProposed)):
        return aggregate_state.with_actor(
            replace(
                actor,
                status=actor_state.ActorStatus.AWAITING_ATTENTION,
                pending_attention_internal=_added(actor.pending_attention_internal, payload.attention_id),
            ),
        )
    if isinstance(payload, (event_work.QuestionAnswered, event_work.PlanResolved)):
        return aggregate_state.with_actor(
            replace(
                actor,
                status=actor_state.ActorStatus.WORKING,
                pending_attention_internal=tuple(
                    pending for pending in actor.pending_attention_internal if pending != payload.attention_id
                ),
            ),
        )
    return None


def _finish_shell_output(
    aggregate_state: contract.AggregateState,
    actor: actor_state.ActorFacts,
    payload: event_shell.ShellOutputFinished,
) -> contract.AggregateState:
    settled = _without_background(actor, payload.shell_id)
    return aggregate_state.with_actor(
        replace(settled, status=_status_after_work_settled(settled)),
    )


def _start_assignment(
    aggregate_state: contract.AggregateState,
    event: event_base.CanonicalEvent[event_base.EventPayload],
    actor: actor_state.ActorFacts,
    payload: event_actor.ActorAssignmentStarted,
) -> contract.AggregateState:
    owner = actor if event.parent_actor_id is None else aggregate_state.actor(event.parent_actor_id)
    if owner is None:
        return aggregate_state
    return aggregate_state.with_actor(
        replace(
            owner,
            status=actor_state.ActorStatus.EXECUTING,
            running_assignment_ids_internal=_added(
                owner.running_assignment_ids_internal,
                payload.assignment_id,
            ),
        ),
    )


def _finish_assignment(
    aggregate_state: contract.AggregateState,
    actor: actor_state.ActorFacts,
    payload: event_actor.ActorAssignmentFinished,
) -> contract.AggregateState:
    owner = _assignment_owner(aggregate_state, actor, payload.assignment_id)
    if owner is None:
        return aggregate_state
    settled = replace(
        owner,
        running_assignment_ids_internal=tuple(
            assignment_id
            for assignment_id in owner.running_assignment_ids_internal
            if assignment_id != payload.assignment_id
        ),
    )
    return aggregate_state.with_actor(
        replace(settled, status=_status_after_work_settled(settled)),
    )


def _assignment_owner(
    aggregate_state: contract.AggregateState,
    event_actor_facts: actor_state.ActorFacts,
    assignment_id: ids.AssignmentId,
) -> actor_state.ActorFacts | None:
    """Find the actor that started one assignment.

    A failed launch can finish on the lead. A successful child assignment
    finishes on the child. The stored assignment id connects both shapes to
    the actor whose status must change.

    Returns:
        The actor facts.

    """
    if assignment_id in event_actor_facts.running_assignment_ids_internal:
        return event_actor_facts
    if event_actor_facts.parent_actor_id is not None:
        parent = aggregate_state.actor(event_actor_facts.parent_actor_id)
        if parent is not None and assignment_id in parent.running_assignment_ids_internal:
            return parent
    return next(
        (
            candidate
            for candidate in aggregate_state.actors.values()
            if assignment_id in candidate.running_assignment_ids_internal
        ),
        None,
    )
