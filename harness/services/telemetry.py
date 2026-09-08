# Copyright (c) 2026 Zhambyl Yermagambet
"""Record pushed telemetry — the daemon-side half of the telemetry channel.

The twin of `HookGatewayService`. A delivery arrives over HTTP as exact bytes,
the harness's own `HarnessTelemetryGateway` says what they meant, and what it
returns is written here. Recording only: translation stays with the
interpreter's next tick, exactly as it does for hooks.

This is what makes the OTLP receiver a thin client instead of a second writer
of the store.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from harness.models.telemetry import (
    HarnessTelemetryRequest,
    TelemetryContext,
)
from harness.registry import HarnessRegistry, HarnessRegistryError

if TYPE_CHECKING:
    from domain.ids import HarnessName, SessionId
    from harness.models.session import (
        Session,
    )
    from repository.contract.facts import RawEventRepository
    from repository.contract.sessions import SessionRepository


class UnknownTelemetryHarnessError(LookupError):
    """Represent unknown telemetry harness."""


class _SessionLookup(TelemetryContext):
    def __init__(self, session_repository: SessionRepository) -> None:
        self.sessions = session_repository

    def find_session(self, session_id: SessionId) -> Session | None:
        return self.sessions.find(session_id)


class TelemetryGatewayService:
    """Represent telemetry gateway service."""

    def __init__(
        self,
        harness_registry: HarnessRegistry,
        raw_event_repository: RawEventRepository,
        session_repository: SessionRepository,
    ) -> None:
        """Initialize the object."""
        self.registry = harness_registry
        self.raw_events = raw_event_repository
        self.context = _SessionLookup(session_repository)

    def record(self, harness: HarnessName, harness_telemetry_request: HarnessTelemetryRequest) -> int:
        """One delivery in, the number of facts it produced out.

        Returns:
            Integer result.

        Raises:
            UnknownTelemetryHarnessError: If no harness owns the telemetry.

        """
        try:
            plugin = self.registry.plugin(harness)
        except HarnessRegistryError as error:
            raise UnknownTelemetryHarnessError(str(error)) from error
        if plugin.telemetry is None:
            message = f"harness accepts no telemetry: {harness}"
            raise UnknownTelemetryHarnessError(message)
        response = plugin.telemetry.receive_telemetry(harness_telemetry_request, self.context)
        if response.raw_events:
            self.raw_events.record(response.raw_events)
        return len(response.raw_events)
