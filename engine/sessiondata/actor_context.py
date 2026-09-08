# Copyright (c) 2026 Zhambyl Yermagambet
"""Actor context."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING, override

from domain import (
    actor_state,
    event_telemetry,
)
from engine.sessiondata import contract

if TYPE_CHECKING:
    from domain import event_base


class ContextWriter(contract.SessionDataWriter):
    """How full the window is, and whether it is being emptied."""

    @override
    def write(
        self,
        canonical_event: event_base.CanonicalEvent[event_base.EventPayload],
        aggregate_state: contract.AggregateState,
    ) -> contract.AggregateState:
        """Write actor context state.

        Returns:
            The aggregate state.

        """
        payload = canonical_event.payload
        actor = aggregate_state.actor(canonical_event.actor_id)
        if actor is None:
            return aggregate_state
        if isinstance(payload, event_telemetry.ContextReported):
            return aggregate_state.with_actor(
                replace(
                    actor,
                    context=actor_state.ActorContext(
                        used_tokens=payload.used_tokens,
                        window_tokens=payload.window_tokens,
                        compacting=actor.context.compacting,
                    ),
                ),
            )
        if isinstance(payload, event_telemetry.CompactionStarted):
            return aggregate_state.with_actor(replace(actor, context=replace(actor.context, compacting=True)))
        if isinstance(payload, event_telemetry.CompactionFinished):
            return aggregate_state.with_actor(
                replace(
                    actor,
                    context=replace(
                        actor.context,
                        compacting=False,
                        used_tokens=(
                            actor.context.used_tokens if payload.after_tokens is None else payload.after_tokens
                        ),
                    ),
                ),
            )
        return aggregate_state
