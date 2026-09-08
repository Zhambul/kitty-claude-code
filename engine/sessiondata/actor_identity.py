# Copyright (c) 2026 Zhambyl Yermagambet
"""Actor identity."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from domain import (
    actor_state,
    event_actor,
    event_session,
    lifecycle,
    messaging,
)
from engine.sessiondata import contract, naming

if TYPE_CHECKING:
    from domain import event_base


class ActorWriter(contract.SessionDataWriter):
    """Who the actors are: their birth, their names, and whether they are done."""

    def __init__(self, model_naming: naming.ModelNaming | None = None) -> None:
        """Initialize the object."""
        self.model_naming = model_naming or naming.ModelNaming()

    def write(
        self,
        canonical_event: event_base.CanonicalEvent[event_base.EventPayload],
        aggregate_state: contract.AggregateState,
    ) -> contract.AggregateState:
        """Write actor identity and lifecycle facts.

        Returns:
            The aggregate state.

        """
        event = canonical_event
        payload = event.payload
        if isinstance(payload, event_session.SessionFinished):
            return _finish_all_actors(aggregate_state, canonical_event.happened_at)
        if isinstance(payload, event_actor.ActorStarted):
            return _start_actor(aggregate_state, event, payload)
        actor = aggregate_state.actor(event.actor_id)
        if actor is None:
            return aggregate_state
        return self._update_actor_state(aggregate_state, actor, event, payload)

    def _update_actor_state(
        self,
        aggregate_state: contract.AggregateState,
        actor: actor_state.ActorFacts,
        event: event_base.CanonicalEvent[event_base.EventPayload],
        payload: event_base.EventPayload,
    ) -> contract.AggregateState:
        changed_actor = _actor_identity_change(actor, event, payload)
        if changed_actor is not None:
            return aggregate_state.with_actor(changed_actor)
        if isinstance(payload, event_session.ModelChanged):
            return self._change_model(aggregate_state, actor, event, payload)
        if isinstance(payload, event_session.EffortChanged):
            state = aggregate_state.with_actor(replace(actor, effort=payload.current))
        else:
            state = aggregate_state
        return state

    def _change_model(
        self,
        aggregate_state: contract.AggregateState,
        actor: actor_state.ActorFacts,
        event: event_base.CanonicalEvent[event_base.EventPayload],
        payload: event_session.ModelChanged,
    ) -> contract.AggregateState:
        if payload.current.name == "<synthetic>":
            return aggregate_state  # a machine-injected record, not a model

        # The display settles HERE, through the harness's one namer, so an
        # unrefined alias ("sonnet") and its later native id show the same
        # name — and a rebuild re-settles history too.
        named_model = self.model_naming.named(event.harness, payload.current)
        return aggregate_state.with_actor(replace(actor, model=named_model))


def _actor_identity_change(
    actor: actor_state.ActorFacts,
    event: event_base.CanonicalEvent[event_base.EventPayload],
    payload: event_base.EventPayload,
) -> actor_state.ActorFacts | None:
    if isinstance(payload, event_actor.ActorNameChanged):
        return replace(actor, name=payload.name)
    if isinstance(payload, event_actor.ActorDescriptionChanged):
        return replace(actor, description=payload.description)
    if isinstance(payload, event_actor.ActorFinished) or (
        isinstance(payload, event_actor.ActorAssignmentFinished) and actor.role != messaging.ActorRole.LEAD
    ):
        return replace(actor, state=lifecycle.LifecycleState.FINISHED, finished_at=event.happened_at)
    if isinstance(payload, event_actor.ActorAssignmentStarted):
        return replace(actor, state=lifecycle.LifecycleState.RUNNING, finished_at=None)
    return None


def _finish_all_actors(
    aggregate_state: contract.AggregateState,
    finished_at: float | None,
) -> contract.AggregateState:
    finished_actors = {
        actor_id: replace(
            actor,
            state=lifecycle.LifecycleState.FINISHED,
            finished_at=finished_at,
        )
        for actor_id, actor in aggregate_state.actors.items()
    }
    return aggregate_state.with_actors(finished_actors)


def _start_actor(
    aggregate_state: contract.AggregateState,
    event: event_base.CanonicalEvent[event_base.EventPayload],
    payload: event_actor.ActorStarted,
) -> contract.AggregateState:
    existing = aggregate_state.actor(event.actor_id)
    born = actor_state.ActorFacts(
        session_id=event.session_id,
        actor_id=event.actor_id,
        role=payload.role,
        name=payload.name,
        state=lifecycle.LifecycleState.RUNNING,
        parent_actor_id=event.parent_actor_id,
        started_at=event.happened_at,
    )
    # An actor announced twice — two raw event streams both saying so —
    # keeps everything already folded about it and only reopens.
    return aggregate_state.with_actor(
        born if existing is None else replace(existing, state=lifecycle.LifecycleState.RUNNING, finished_at=None),
    )
