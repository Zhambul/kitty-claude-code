# Copyright (c) 2026 Zhambyl Yermagambet
"""Base types for canonical event payloads and envelopes."""

from dataclasses import dataclass

from domain.ids import (
    ActorId,
    CanonicalEventId,
    HarnessName,
    RawEventId,
    SessionId,
    TurnId,
    WindowId,
)
from domain.stored import STORED


@dataclass(frozen=True)
class EventPayload:
    """Provide stored-shape rules for every canonical payload."""

    __pydantic_config__ = STORED


@dataclass(frozen=True)
class CanonicalEvent[EventPayloadType: EventPayload]:
    """Hold one canonical fact and its storage metadata."""

    event_id: CanonicalEventId
    session_id: SessionId
    actor_id: ActorId
    turn_id: TurnId | None
    parent_actor_id: ActorId | None
    harness: HarnessName
    occurred_at: float | None
    terminal_window_id: WindowId | None
    harness_process_id: int | None
    payload: EventPayloadType
    cursor: int | None = None
    accepted_at: float | None = None
    raw_event_ids: tuple[RawEventId, ...] = ()

    __pydantic_config__ = STORED

    @property
    def happened_at(self) -> float:
        """Source time, or storage acceptance time.

        Raises:
            ValueError: If an input value is not valid.

        """
        if self.occurred_at is not None:
            return self.occurred_at
        if self.accepted_at is not None:
            return self.accepted_at
        message = "an event that is not stored has no happened_at"
        raise ValueError(message)
