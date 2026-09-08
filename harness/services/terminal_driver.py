# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the harness terminal driver."""

from domain.ids import WindowId
from harness.contract import ComposerDriver
from harness.services.terminal_driver_panes import TerminalPaneDriver
from harness.services.terminal_driver_text import TerminalTextDriver
from harness.services.terminal_driver_values import native_window_id
from terminal.contract import TerminalPlugin
from terminal.models.viewport import ScreenReadRequest


class TerminalDriver(TerminalTextDriver, TerminalPaneDriver, ComposerDriver):
    """Convert harness values to terminal requests."""

    def __init__(self, terminal_plugin: TerminalPlugin) -> None:
        """Initialize the object."""
        self.terminal = terminal_plugin

    def read_text(
        self,
        window_id: WindowId,
        extent: str = "screen",
        *,
        ansi: bool = False,
    ) -> str | None:
        """Read visible text from a terminal window.

        Returns:
            Screen text, or None if the read fails or the requested extent is not supported.

        """
        if extent != "screen":
            return None
        response = self.terminal.viewport.read_screen(ScreenReadRequest(native_window_id(window_id), ansi=ansi))
        return response.text if response.succeeded else None
