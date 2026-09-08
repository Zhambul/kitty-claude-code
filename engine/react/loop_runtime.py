# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide reaction-loop runtime operations."""

from collections.abc import Callable
from contextlib import ExitStack
from typing import Protocol

from audit.failures import FailureContext
from domain import event_base, ids as domain_ids
from engine.react.loop_context import ReactionLoopContext
from engine.sessiondata import contract as sessiondata_contract
from engine.sessiondata.actor_batch import AppliedActorBatch

REACTION_BATCH_SIZE = 500


def _notify_actor_batch(
    applied_actor_batch: AppliedActorBatch,
    listeners: tuple[sessiondata_contract.AppliedActorListener, ...],
    audit_failure: Callable[[str, FailureContext], None],
) -> None:
    for session_id, actors in applied_actor_batch.actors.items():
        for listener in listeners:
            try:
                listener.applied(session_id, tuple(actors.values()))
            except Exception:  # noqa: BLE001 - Record each listener failure and continue other listeners.
                audit_failure(type(listener).__name__, FailureContext(session_id=session_id))


class _ReactionLoopRuntimeContext(ReactionLoopContext, Protocol):
    def tick(self, listeners: tuple[sessiondata_contract.AppliedActorListener, ...] | None = None) -> int:
        """React to and materialize one event batch."""

    def _react(self, canonical_event: event_base.CanonicalEvent[event_base.EventPayload]) -> None:
        """Apply side-effect reactions."""

    def _materialize(
        self,
        canonical_event: event_base.CanonicalEvent[event_base.EventPayload],
        states: dict[domain_ids.SessionId, sessiondata_contract.AggregateState],
        listeners: tuple[sessiondata_contract.AppliedActorListener, ...],
    ) -> None:
        """Apply an event to the read model."""

    def _audit_failure(self, where: str, failure_context: FailureContext) -> None:
        """Record a recoverable failure."""

    def _replay_events(self, canonical_events: tuple[event_base.CanonicalEvent[event_base.EventPayload], ...]) -> None:
        """Materialize replay events without listeners."""


class ReactionLoopRuntime:
    """Provide reaction-loop runtime operations."""

    def tick(
        self: _ReactionLoopRuntimeContext,
        listeners: tuple[sessiondata_contract.AppliedActorListener, ...] | None = None,
    ) -> int:
        """React to and materialize one event batch.

        Returns:
            The number of processed events.

        """
        session_data = self.dependencies.session_data_repository
        events = self.dependencies.canonical_event_repository.page_from(session_data.progress(), REACTION_BATCH_SIZE)
        states: dict[domain_ids.SessionId, sessiondata_contract.AggregateState] = {}
        applied_listeners = self.dependencies.listeners if listeners is None else listeners
        for canonical_event in events:
            self._react(canonical_event)
            self._materialize(canonical_event, states, applied_listeners)
        return len(events)

    def drain(self: _ReactionLoopRuntimeContext, cancelled: Callable[[], bool]) -> int:
        """Fold ready history before announcing the final display state.

        Returns:
            The number of processed events across all batches.

        """
        batch = AppliedActorBatch()
        total = 0
        with self.dependencies.changes.batch(), ExitStack() as cleanup:
            cleanup.callback(_notify_actor_batch, batch, self.dependencies.listeners, self._audit_failure)
            while not cancelled():
                count = self.tick((batch,))
                if not count:
                    break
                total += count
        return total

    def rebuild(self: _ReactionLoopRuntimeContext) -> int:
        """Rebuild the read model without side effects.

        Returns:
            The number of stored events used for the rebuild.

        """
        repository = self.dependencies.canonical_event_repository
        session_data = self.dependencies.session_data_repository
        session_data.clear()
        total = 0
        while True:
            events = repository.page_from(session_data.progress(), REACTION_BATCH_SIZE)
            if not events:
                return total
            self._replay_events(events)
            total += len(events)

    def _replay_events(
        self: _ReactionLoopRuntimeContext,
        canonical_events: tuple[event_base.CanonicalEvent[event_base.EventPayload], ...],
    ) -> None:
        states: dict[domain_ids.SessionId, sessiondata_contract.AggregateState] = {}
        for canonical_event in canonical_events:
            self._materialize(canonical_event, states, ())
