# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide terminal session test data."""

from __future__ import annotations

from typing import TYPE_CHECKING

from domain.ids import SessionId, WindowId as SessionWindowId

if TYPE_CHECKING:
    from collections.abc import Mapping


class FakeSessions:
    """Provide terminal window identifiers by session."""

    def __init__(
        self,
        windows_by_session: Mapping[str, SessionWindowId | str] | None = None,
    ) -> None:
        """Initialize the object."""
        self.windows_by_session = {
            session_id: SessionWindowId(str(window_id)) for session_id, window_id in (windows_by_session or {}).items()
        }

    def find(self, session_id: SessionId) -> _SessionRow | None:
        """Find one session row.

        Returns:
            The stored window row, or None if the session has no window.

        """
        window_id = self.windows_by_session.get(str(session_id))
        return None if window_id is None else _SessionRow(window_id)


class _SessionRow:
    """Contain the stored terminal window identifier."""

    def __init__(self, terminal_window_id: SessionWindowId | None) -> None:
        """Initialize the object."""
        self.terminal_window_id = terminal_window_id
