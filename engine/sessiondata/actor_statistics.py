# Copyright (c) 2026 Zhambyl Yermagambet
"""Actor statistics."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING, override

from engine.sessiondata import contract

if TYPE_CHECKING:
    from domain import (
        actor_state,
        event_base,
    )

from engine.sessiondata.actor_statistics_support import _conversation_counted, _timed, _tool_event_counted


class StatisticsWriter(contract.SessionDataWriter):
    """The scoreboard: what the actor did, counted once as it happened.

    `active_seconds` counts CLOSED intervals only — a prompt to the end of the
    turn it started. The interval still open has no length until somebody asks,
    so the route that answers adds it; storing a number that grows on its own
    would mean writing a row per second.
    """

    @override
    def write(
        self,
        canonical_event: event_base.CanonicalEvent[event_base.EventPayload],
        aggregate_state: contract.AggregateState,
    ) -> contract.AggregateState:
        """Write actor activity statistics.

        Returns:
            The aggregate state.

        """
        event = canonical_event
        payload = event.payload
        actor = aggregate_state.actor(event.actor_id)
        if actor is None:
            return aggregate_state
        statistics = _counted(actor.statistics, payload)
        statistics = _timed(statistics, canonical_event)
        if statistics == actor.statistics:
            return aggregate_state
        return aggregate_state.with_actor(replace(actor, statistics=statistics))


def _counted(
    actor_statistics: actor_state.ActorStatistics, event_payload: event_base.EventPayload,
) -> actor_state.ActorStatistics:
    counted = _conversation_counted(actor_statistics, event_payload)
    if counted is not None:
        return counted
    return _tool_event_counted(actor_statistics, event_payload)
