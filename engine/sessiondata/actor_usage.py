# Copyright (c) 2026 Zhambyl Yermagambet
"""Actor usage."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING, override

from domain import (
    actor_state,
    event_telemetry,
)
from engine.sessiondata import contract

if TYPE_CHECKING:
    from decimal import Decimal

    from domain import event_base


class UsageWriter(contract.SessionDataWriter):
    """Tokens and money, cumulatively.

    A harness reports usage either as a running total or as one response's
    share, and it says which — so a total REPLACES and a share ADDS, and
    treating them alike is how a session's cost silently doubles.
    """

    @override
    def write(
        self,
        canonical_event: event_base.CanonicalEvent[event_base.EventPayload],
        aggregate_state: contract.AggregateState,
    ) -> contract.AggregateState:
        """Write actor usage totals.

        Returns:
            The aggregate state.

        """
        payload = canonical_event.payload
        if not isinstance(payload, event_telemetry.UsageReported):
            return aggregate_state
        actor = aggregate_state.actor(canonical_event.actor_id)
        if actor is None:
            return aggregate_state
        usage = actor.usage
        tokens = payload.tokens if payload.cumulative else usage.tokens + payload.tokens
        cost = _cost(
            usage.cost_in_usd,
            payload.cost_in_usd,
            cumulative=payload.cumulative,
        )
        return aggregate_state.with_actor(replace(actor, usage=actor_state.ActorUsage(tokens, cost)))


def _cost(
    known: Decimal | None,
    reported: Decimal | None,
    *,
    cumulative: bool,
) -> Decimal | None:
    if reported is None:
        return known
    if cumulative or known is None:
        return reported
    return known + reported
