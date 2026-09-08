# Copyright (c) 2026 Zhambyl Yermagambet
"""Correlate a verified Codex rewind with its next native session."""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from typing import TYPE_CHECKING

from domain.ids import SessionId

if TYPE_CHECKING:
    from domain.ids import WindowId

PENDING_SECONDS = 600.0


@dataclass(frozen=True)
class PendingRewind:
    """Represent pending rewind."""

    session_id: SessionId
    expires_at: float


class RewindContinuity:
    """Join the control gesture to a new session in the same terminal.

    Codex 0.149 starts a new session after a native transcript rewind, but its
    session metadata does not name the prior session. The control has both the
    prior session and the terminal. The next session start has the new session
    and the same terminal. This small registry joins those two facts.
    """

    def __init__(self) -> None:
        """Initialize the object."""
        self._lock = threading.Lock()
        self._pending_by_window: dict[WindowId, PendingRewind] = {}
        self._resolved_by_session: dict[SessionId, SessionId] = {}

    def expect(
        self,
        session_id: SessionId,
        window_id: WindowId,
        *,
        now: float | None = None,
    ) -> None:
        """Return the expect."""
        observed_at = time.monotonic() if now is None else now
        with self._lock:
            self._pending_by_window[window_id] = PendingRewind(
                session_id,
                observed_at + PENDING_SECONDS,
            )

    def resolve(
        self,
        session_id: SessionId,
        window_id: WindowId | None,
        *,
        declared_from: SessionId | None = None,
        now: float | None = None,
    ) -> SessionId | None:
        """Resolve resolve.

        Returns:
            The session id.

        """
        observed_at = time.monotonic() if now is None else now
        with self._lock:
            if declared_from is not None:
                self._resolved_by_session[session_id] = declared_from
                return declared_from
            resolved = self._resolved_by_session.get(session_id)
            if resolved is not None:
                return resolved
            return self._resolve_pending(session_id, window_id, observed_at)

    def pending(
        self,
        session_id: SessionId,
        window_id: WindowId,
        *,
        now: float | None = None,
    ) -> bool:
        """Return the pending.

        True while this window waits for its rewind continuation.

        Returns:
            Pending.

        """
        observed_at = time.monotonic() if now is None else now
        with self._lock:
            pending = self._pending_by_window.get(window_id)
            if pending is None:
                return False
            if pending.expires_at < observed_at:
                self._pending_by_window.pop(window_id, None)
                return False
            return pending.session_id == session_id

    def release(self, session_id: SessionId) -> None:
        """Release a completed rewind relation."""
        with self._lock:
            self._resolved_by_session.pop(session_id, None)

    def _resolve_pending(
        self,
        session_id: SessionId,
        window_id: WindowId | None,
        observed_at: float,
    ) -> SessionId | None:
        if window_id is None:
            return None
        pending = self._pending_by_window.get(window_id)
        if pending is None:
            return None
        if pending.expires_at < observed_at:
            self._pending_by_window.pop(window_id, None)
            return None
        if pending.session_id == session_id:
            return None
        self._pending_by_window.pop(window_id, None)
        self._resolved_by_session[session_id] = pending.session_id
        return pending.session_id
