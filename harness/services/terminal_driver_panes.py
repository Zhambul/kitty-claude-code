# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide terminal pane driver operations."""

from domain.ids import WindowId
from harness.services.terminal_driver_values import native_window_id
from terminal.contract import TerminalPlugin
from terminal.models.panes import PaneResizeRequest, SplitAxis


class TerminalPaneDriver:
    """Provide terminal pane driver operations."""

    terminal: TerminalPlugin

    def lines(self, window_id: WindowId) -> int | None:
        """Return the line count of a terminal window.

        Returns:
            The line count of a terminal window.

        """
        native = native_window_id(window_id)
        return next(
            (window.lines for window in self.terminal.metadata.windows() if window.window_id == native),
            None,
        )

    def resize_lines(self, window_id: WindowId, cells: int) -> bool:
        """Resize a terminal window by line count.

        Returns:
            True if the terminal reports a successful resize.

        """
        response = self.terminal.panes.resize_pane(
            PaneResizeRequest(native_window_id(window_id), SplitAxis.VERTICAL, cells),
        )
        return response.succeeded
