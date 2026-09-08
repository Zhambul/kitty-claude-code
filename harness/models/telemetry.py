# Copyright (c) 2026 Zhambyl Yermagambet
"""Pushed telemetry: raw events a harness reports out-of-band.

The twin of the hook channel. A hook delivery is the harness's own stdin at a
lifecycle moment; a telemetry delivery is a side channel a harness exposes —
OTLP metrics on a local port, rate limits on a status-line command's stdin —
that carries facts no hook payload contains.

The client sends exact bytes to the daemon. Nothing outside the daemon writes
the store.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

from harness.models.raw_events import RawEvent

if TYPE_CHECKING:
    from domain.ids import SessionId
    from harness.models.session import Session

# The channel's own header vocabulary, read only by the endpoint and stamped
# only by the clients that ship a delivery.
TELEMETRY_KIND_HEADER = "X-Baqylau-Telemetry-Kind"


@dataclass(frozen=True)
class HarnessTelemetryRequest:
    """One delivery: which side channel it came from, and its exact bytes."""

    kind: str
    payload: bytes


@dataclass(frozen=True)
class HarnessTelemetryResponse:
    """The raw events from one telemetry delivery."""

    raw_events: tuple[RawEvent, ...] = ()


class TelemetryContext(Protocol):
    """What a gateway may ask the application while interpreting a delivery.

    Only the session lookup: a telemetry document names sessions by id and the
    gateway has to resolve them, but resolving them is not the gateway's job to
    implement.
    """

    def find_session(self, session_id: SessionId) -> Session | None:
        """Return session."""
        ...
