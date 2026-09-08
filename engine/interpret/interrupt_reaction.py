# Copyright (c) 2026 Zhambyl Yermagambet
"""Clear interrupt state after a turn ends."""

from __future__ import annotations

from typing import TYPE_CHECKING

from domain.event_conversation import TurnAborted, TurnFinished
from harness.contract import CanonicalEventReaction

if TYPE_CHECKING:
    from domain.event_base import CanonicalEvent, EventPayload
    from harness.models.interrupts import InterruptRegistry


class InterruptCanonicalEventReaction(CanonicalEventReaction):
    """Clear the interrupt mark after any turn-end event."""

    def __init__(self, interrupt_registry: InterruptRegistry) -> None:
        """Initialize the object."""
        self.interrupts = interrupt_registry

    def react(self, canonical_event: CanonicalEvent[EventPayload]) -> None:
        """Clear interrupt state when the turn ends."""
        payload = canonical_event.payload
        if isinstance(payload, (TurnFinished, TurnAborted)):
            self.interrupts.clear(canonical_event.session_id)
