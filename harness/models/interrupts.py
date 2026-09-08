# Copyright (c) 2026 Zhambyl Yermagambet
"""Tracking for an interrupt no native raw event has corroborated yet.

An interrupt is a screen heuristic (an escape key sent, the screen stopped
changing) — some harnesses' raw event streams carry no record distinguishing
a turn cut short from one that finished on its own, so nothing canonical
ever settles the turn. `HarnessControlService` marks this registry exactly
when a control's `InterruptResult` says `acknowledged` but not `corroborated`;
a harness whose own translator will pick up a native abort record on its own
next read never marks it at all. `engine.interpret.interrupts` reads it back
to emit the one fallback fact this registry exists for.
"""

from __future__ import annotations

import threading
import time
from typing import TYPE_CHECKING

from harness.services.control_contract import InterruptMarker

if TYPE_CHECKING:
    from collections.abc import Callable

    from domain.ids import SessionId


class InterruptRegistry(InterruptMarker):
    """One process, one registry: which sessions have an unsettled interrupt.

    Written by control-request HTTP threads (`mark`, `clear`); read by the
    interpreter thread. The lock is the only thing making that safe.
    """

    def __init__(self, on_mark: Callable[[float], None] | None = None) -> None:
        """Initialize the object."""
        self._lock = threading.Lock()
        self._marked_at: dict[SessionId, float] = {}
        self._on_mark = on_mark

    def mark(self, session_id: SessionId) -> None:
        """Mark."""
        marked_at = time.time()
        with self._lock:
            self._marked_at[session_id] = marked_at
        if self._on_mark is not None:
            self._on_mark(marked_at)

    def clear(self, session_id: SessionId) -> None:
        """Clear clear."""
        with self._lock:
            self._marked_at.pop(session_id, None)

    def pending(self, session_id: SessionId) -> float | None:
        """Return the pending.

        Returns:
            Pending.

        """
        with self._lock:
            return self._marked_at.get(session_id)
