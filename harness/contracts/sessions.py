# Copyright (c) 2026 Zhambyl Yermagambet
"""Define terminal session discovery and resume contracts."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

from terminal.models.values import SESSION_WINDOW_TAG, WindowInfo

if TYPE_CHECKING:
    from domain.ids import HarnessName, SessionId, WindowId
    from harness.models.session import LocatedSession

type TerminalWindows = tuple[WindowInfo, ...]


def terminal_window_session(window_info: WindowInfo) -> str | None:
    """Return the session tag from one terminal window.

    Returns:
        The session tag.

    """
    return window_info.tags.get(SESSION_WINDOW_TAG)


class HarnessResumeLocator(Protocol):
    """Find native resume commands in terminal process data."""

    def locate(self, windows: tuple[WindowInfo, ...]) -> tuple[LocatedSession, ...]:
        """Locate resumable sessions."""
        ...


class SessionTerminalState(Protocol):
    """Provide terminal data for resume discovery and liveness."""

    def windows(self) -> tuple[WindowInfo, ...]:
        """Return terminal windows."""
        ...

    def window_for_session(self, session_id: SessionId) -> WindowId | None:
        """Return the window for a session."""
        ...

    def window_is_live(
        self,
        session_id: SessionId,
        window_id: WindowId,
        windows: tuple[WindowInfo, ...],
    ) -> bool:
        """Return true if the session window is live."""
        ...


class SessionResumeRecorder(Protocol):
    """Record one confirmed or discovered resume launch."""

    def resumed(
        self,
        harness: HarnessName,
        session_id: SessionId,
        window_id: WindowId,
    ) -> None:
        """Record a session resume."""
        ...
