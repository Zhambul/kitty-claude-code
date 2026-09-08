# Copyright (c) 2026 Zhambyl Yermagambet
"""Write the session goal."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING, override

from domain.event_work import GoalChanged
from domain.session_state import SessionGoal
from engine.sessiondata.contract import AggregateState, SessionDataWriter

if TYPE_CHECKING:
    from domain.event_base import CanonicalEvent, EventPayload


class GoalWriter(SessionDataWriter):
    """Write the session objective and its native-independent state."""

    @override
    def write(
        self,
        canonical_event: CanonicalEvent[EventPayload],
        aggregate_state: AggregateState,
    ) -> AggregateState:
        """Write the event into the session goal.

        Returns:
            State with the goal updated or cleared, or unchanged state when the event does not apply.

        """
        payload = canonical_event.payload
        if not isinstance(payload, GoalChanged) or aggregate_state.session is None:
            return aggregate_state
        if payload.state == "cleared":
            return replace(aggregate_state, session=replace(aggregate_state.session, goal=None))
        return replace(
            aggregate_state,
            session=replace(
                aggregate_state.session,
                goal=SessionGoal(payload.objective, payload.state, payload.reason),
            ),
        )
