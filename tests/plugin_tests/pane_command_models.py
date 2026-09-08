# Copyright (c) 2026 Zhambyl Yermagambet
"""Pane command fakes for terminal plugin tests."""

from __future__ import annotations

from typing import TYPE_CHECKING

from audit.documents import AuditContent
from terminal.adapter import SessionTerminalResult
from tests.plugin_tests import vocabulary as fixture
from tests.plugin_tests.terminal_plugin_values import PRIMARY_SESSION

if TYPE_CHECKING:
    from domain.ids import SessionId, WindowId

type PaneAuditRow = tuple[str, AuditContent]


class RecordingPaneTerminal:
    """Record pane commands for service assertions."""

    def __init__(self) -> None:
        """Create empty records for pane queries and commands."""
        self.session_windows: list[WindowId | None] = []
        self.toggles: list[tuple[SessionId, int]] = []
        self.resizes: list[tuple[SessionId, int]] = []
        self.widths: list[tuple[SessionId, int]] = []
        self.geometry_sessions: list[SessionId] = []

    def session_for_window(self, window_id: WindowId | None) -> SessionId:
        """Record and check the expected window identity.

        Returns:
            The fixed test session identity.

        """
        self.session_windows.append(window_id)
        assert window_id == fixture.SEVENTY_SEVEN_TEXT
        return PRIMARY_SESSION

    def toggle_session_panes(
        self,
        session_id: SessionId,
        width_percent: int,
    ) -> SessionTerminalResult:
        """Record a pane toggle request.

        Returns:
            A successful terminal result.

        """
        self.toggles.append((session_id, width_percent))
        return SessionTerminalResult(succeeded=True)

    def resize_activity_pane(
        self,
        session_id: SessionId,
        columns: int,
    ) -> SessionTerminalResult:
        """Record a pane resize request.

        Returns:
            A successful terminal result.

        """
        self.resizes.append((session_id, columns))
        return SessionTerminalResult(succeeded=True)

    def activity_pane_geometry(self, session_id: SessionId) -> tuple[int, int]:
        """Record a geometry query.

        Returns:
            The fixed pane and total column counts.

        """
        self.geometry_sessions.append(session_id)
        return (fixture.PANE_WIDTH_PERCENT, 100)

    def set_activity_pane_width(
        self,
        session_id: SessionId,
        width_percent: int,
    ) -> SessionTerminalResult:
        """Record a pane width request.

        Returns:
            A successful terminal result.

        """
        self.widths.append((session_id, width_percent))
        return SessionTerminalResult(succeeded=True)


class PaneAuditRecorder:
    """Record pane command audit writes."""

    def __init__(self, rows: list[PaneAuditRow]) -> None:
        """Keep the list that receives audit actions and content."""
        self._rows = rows

    def state_file(
        self,
        log: str,
        path: str,
        action: str,
        content: AuditContent = "",
    ) -> None:
        """Record the audit location, action, and content."""
        self.last_location = (log, path)
        self._rows.append((action, content))
