# Copyright (c) 2026 Zhambyl Yermagambet
"""Claude Code's reactions to its own committed facts, run by the interpreter.

The interpreter dispatches by the event's harness, so no implementation here
carries a harness check. Instances live on the plugin descriptor (built at
import with no dependencies); the control service arrives per call, because it
only exists inside the daemon.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, override

from domain.event_session import SessionStarted
from harness.contract import HarnessCanonicalEventReactor, HarnessReactorContext
from harness.impl.claude_code.otel import launch as otel

if TYPE_CHECKING:
    from domain.event_base import CanonicalEvent, EventPayload


class ClaudeOtelCanonicalEventReactor(HarnessCanonicalEventReactor):
    """Represent claude otel canonical event reactor."""

    @override
    def react(
        self,
        canonical_event: CanonicalEvent[EventPayload],
        harness_reactor_context: HarnessReactorContext,
    ) -> None:
        """Return the react."""
        if isinstance(canonical_event.payload, SessionStarted):
            otel.start()
