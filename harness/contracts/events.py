# Copyright (c) 2026 Zhambyl Yermagambet
"""Define harness event input and reaction contracts."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from domain.event_base import CanonicalEvent, EventPayload
    from domain.ids import SessionId
    from harness.models.hooks import HarnessHookRequest, HarnessHookResponse
    from harness.models.raw_events import RawEvent, TranslationResult
    from harness.models.session import Session
    from harness.models.telemetry import (
        HarnessTelemetryRequest,
        HarnessTelemetryResponse,
        TelemetryContext,
    )


class HarnessRawEventSource(Protocol):
    """Read one native event feed after a resume position."""

    source_identity: str

    def watch_paths(self) -> tuple[str, ...]:
        """List files that can stay open between writes.

        Returns:
            File input paths, or no paths for a non-file source.

        """
        return ()

    def read(self, after_position: str | None) -> tuple[RawEvent, ...]:
        """Read raw events after the source position."""
        ...


class HarnessRawEventSources(Protocol):
    """Create and release raw-event sources for a session."""

    def for_session(self, session: Session) -> tuple[HarnessRawEventSource, ...]:
        """Return sources for the session."""
        ...

    def release_session(self, session_id: SessionId) -> None:
        """Release source readers for the session."""
        ...


class HarnessHookGateway(Protocol):
    """Convert one pushed hook delivery into raw events and a reply."""

    def receive_hook(
        self,
        harness_hook_request: HarnessHookRequest,
    ) -> HarnessHookResponse:
        """Receive one hook delivery."""
        ...


class HarnessTelemetryGateway(Protocol):
    """Convert one pushed telemetry delivery into raw events."""

    def receive_telemetry(
        self,
        harness_telemetry_request: HarnessTelemetryRequest,
        telemetry_context: TelemetryContext,
    ) -> HarnessTelemetryResponse:
        """Receive one telemetry delivery."""
        ...


class HarnessTranslator(Protocol):
    """Translate harness-native raw events."""

    def translate(self, raw_event: RawEvent) -> TranslationResult:
        """Translate one raw event."""
        ...

    def release_session(self, session_id: SessionId) -> None:
        """Release transient session state."""
        ...


class CoreTranslator(Protocol):
    """Translate raw events from Baqylau services."""

    def translate(self, raw_event: RawEvent) -> TranslationResult:
        """Translate one raw event."""
        ...


class CanonicalEventReaction(Protocol):
    """React to every committed canonical event in order."""

    def react(self, canonical_event: CanonicalEvent[EventPayload]) -> None:
        """React to one canonical event."""
        ...
