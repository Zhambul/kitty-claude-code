# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide reaction-loop side-effect operations."""

from typing import Protocol

from audit.failures import FailureContext
from domain import event_base
from engine.react.loop_context import ReactionLoopContext


def _context(canonical_event: event_base.CanonicalEvent[event_base.EventPayload]) -> FailureContext:
    return FailureContext(
        session_id=canonical_event.session_id,
        event_id=canonical_event.event_id,
        cursor=canonical_event.cursor,
    )


class _ReactionLoopEffectsContext(ReactionLoopContext, Protocol):
    def _audit_failure(self, where: str, failure_context: FailureContext) -> None:
        """Record a recoverable failure."""


class ReactionLoopEffects:
    """Provide side-effect reaction operations."""

    def _react(
        self: _ReactionLoopEffectsContext, canonical_event: event_base.CanonicalEvent[event_base.EventPayload],
    ) -> None:
        for reaction in self.dependencies.reactions:
            try:
                reaction.react(canonical_event)
            except Exception:  # noqa: BLE001 -- Record one failed reaction and let the other reactions run.
                self._audit_failure(type(reaction).__name__, _context(canonical_event))
        try:
            reactors = self.dependencies.harness_registry.plugin(canonical_event.harness).reactors
        except Exception:  # noqa: BLE001 -- Record plugin lookup failures without stopping the event worker.
            self._audit_failure("harness lookup", _context(canonical_event))
            return
        context = self.dependencies.harness_reactor_context
        if context is None:
            if reactors:
                self._audit_failure("harness reactor context", _context(canonical_event))
            return
        for reactor in reactors:
            try:
                reactor.react(canonical_event, context)
            except Exception:  # noqa: BLE001 -- Isolate each harness reactor and record its failure.
                self._audit_failure(type(reactor).__name__, _context(canonical_event))

    def _audit_failure(self: _ReactionLoopEffectsContext, where: str, failure_context: FailureContext) -> None:
        self.failures.record(where, failure_context)
