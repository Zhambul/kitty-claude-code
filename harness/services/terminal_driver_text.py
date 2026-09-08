# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide terminal text-input driver operations."""

from domain.ids import WindowId
from harness.services.terminal_driver_values import native_window_id
from terminal.contract import TerminalPlugin
from terminal.models.input import KeySendRequest, TextInputMode, TextInsertRequest, TextSubmitRequest


class TerminalTextDriver:
    """Provide terminal text-input driver operations."""

    terminal: TerminalPlugin

    def send_key(self, window_id: WindowId, *keys: str) -> bool:
        """Send keys to a terminal window, stopping at the first failure.

        Returns:
            True if every key was sent successfully, including when no keys were supplied.

        """
        native = native_window_id(window_id)
        return all(
            self.terminal.input.send_key(KeySendRequest(native, str(key))).succeeded
            for key in keys
        )

    def insert_text(self, window_id: WindowId, text: str, *, paste: bool = True) -> bool:
        """Insert text into a terminal window.

        Returns:
            True if the terminal reports a successful insertion.

        """
        mode = TextInputMode.PASTE if paste else TextInputMode.TYPE
        request = TextInsertRequest(native_window_id(window_id), str(text), mode)
        response = self.terminal.input.insert_text(request)
        return response.succeeded

    def submit_text(self, window_id: WindowId, text: str, *, paste: bool = True) -> bool:
        """Submit text to a terminal window.

        Returns:
            True if the terminal reports a successful submission.

        """
        mode = TextInputMode.PASTE if paste else TextInputMode.TYPE
        request = TextSubmitRequest(native_window_id(window_id), str(text), mode)
        response = self.terminal.input.submit_text(request)
        return response.succeeded

    def send_text(self, window_id: WindowId, text: str) -> bool:
        """Submit text as typed input.

        Returns:
            True if the terminal reports a successful submission.

        """
        return self.submit_text(window_id, text, paste=False)

    def paste_text(self, window_id: WindowId, text: str) -> bool:
        """Submit text as pasted input.

        Returns:
            True if the terminal reports a successful submission.

        """
        return self.submit_text(window_id, text, paste=True)
