# Copyright (c) 2026 Zhambyl Yermagambet
"""Kitty terminal text and key input adapter."""

from terminal.contract import TerminalInput
from terminal.impl.kitty import match, remote as kitty_remote_api
from terminal.models.input import (
    KeySendRequest,
    KeySendResponse,
    TextInputMode,
    TextInsertRequest,
    TextInsertResponse,
    TextSubmitRequest,
    TextSubmitResponse,
)

MATCH_OPTION = "--match"


class KittyInput(TerminalInput):
    """Represent Kitty input operations."""

    def __init__(self, kitty_remote: kitty_remote_api.KittyRemote) -> None:
        """Initialize the input adapter."""
        self.kitty_remote = kitty_remote

    def insert_text(self, text_insert_request: TextInsertRequest) -> TextInsertResponse:
        """Insert text into one Kitty window.

        Returns:
            The insertion result with a reason if delivery fails.

        """
        delivered = self.kitty_remote.insert_text(
            text_insert_request.window_id,
            text_insert_request.text,
            bracketed=text_insert_request.mode == TextInputMode.PASTE,
        )
        return TextInsertResponse(delivered, None if delivered else "terminal input failed")

    def submit_text(self, text_submit_request: TextSubmitRequest) -> TextSubmitResponse:
        """Submit text to one Kitty window.

        Returns:
            The submission result with a reason if delivery fails.

        """
        delivered = self.kitty_remote.send_text(
            text_submit_request.window_id,
            text_submit_request.text,
            bracketed=text_submit_request.mode == TextInputMode.PASTE,
        )
        return TextSubmitResponse(delivered, None if delivered else "terminal input failed")

    def send_key(self, key_send_request: KeySendRequest) -> KeySendResponse:
        """Send one key event to a Kitty window.

        Returns:
            The key delivery result with a reason on failure.

        """
        succeeded = not self.kitty_remote.run(
            "send-key", MATCH_OPTION, match.window(key_send_request.window_id), _key_name(key_send_request.key),
        )
        return KeySendResponse(succeeded, None if succeeded else "terminal key input failed")


def _key_name(key: str) -> str:
    return "esc" if key == "escape" else key
