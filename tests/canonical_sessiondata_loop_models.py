# Copyright (c) 2026 Zhambyl Yermagambet
"""Canonical sessiondata loop models."""

from __future__ import annotations

import typing

from tests import canonical_sessiondata_components as sessiondata_components

if typing.TYPE_CHECKING:
    from audit.documents import AuditContent
    from tests.canonical_sessiondata_components import domain as session_domain


class RecordingReaction(sessiondata_components.harness.contract.CanonicalEventReaction):
    """Represent recording reaction."""

    def __init__(self) -> None:
        """Create an empty reaction record."""
        self.seen: list[str] = []

    def react(self, canonical_event: session_domain.event_base.CanonicalEvent) -> None:
        """Process react."""
        self.seen.append(str(canonical_event.event_id))


class _NoReactorPlugin:
    reactors: tuple[sessiondata_components.harness.contract.HarnessCanonicalEventReactor, ...] = ()


class NoReactors:
    """Represent no reactors."""

    def __init__(self) -> None:
        """Initialize the registry."""
        self.harnesses: list[session_domain.ids.HarnessName] = []

    def plugin(self, harness: session_domain.ids.HarnessName) -> _NoReactorPlugin:
        """Record the plugin query.

        Returns:
            A plugin with no reactors.

        """
        self.harnesses.append(harness)
        return _NoReactorPlugin()


class RecordingAudit:
    """Represent recording audit."""

    def __init__(self) -> None:
        """Create empty audit records."""
        self.failures: list[tuple[str, AuditContent]] = []
        self.sources: list[str] = []

    def error(
        self,
        session_or_log: str = "",
        func: str = "",
        context: AuditContent = None,
    ) -> None:
        """Process error."""
        self.sources.append(session_or_log)
        self.failures.append((func, context))


class BrokenWriter:
    """Fail each write to test loop error handling."""

    def write(
        self,
        canonical_event: session_domain.event_base.CanonicalEvent[session_domain.event_base.EventPayload],
        state: sessiondata_components.engine.contract.AggregateState,
    ) -> typing.Never:
        """Record the input and fail the write.

        Raises:
            RuntimeError: For every event.

        """
        self.failure = (canonical_event, state)
        message = "cannot project event"
        raise RuntimeError(message)
