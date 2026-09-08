# Copyright (c) 2026 Zhambyl Yermagambet
"""Kitty terminal viewport adapter."""

from terminal.contract import TerminalViewport
from terminal.impl.kitty import match, remote as kitty_remote_api
from terminal.models.viewport import ScreenReadRequest, ScreenReadResponse


class KittyViewport(TerminalViewport):
    """Represent Kitty viewport operations."""

    def __init__(self, kitty_remote: kitty_remote_api.KittyRemote) -> None:
        """Initialize the viewport adapter."""
        self.kitty_remote = kitty_remote

    def read_screen(self, screen_read_request: ScreenReadRequest) -> ScreenReadResponse:
        """Return the visible screen text for one Kitty window.

        Returns:
            The visible screen text for one Kitty window.

        """
        payload = kitty_remote_api.GetTextRcPayload(
            match=match.window(screen_read_request.window_id), extent="screen", ansi=screen_read_request.ansi,
        )
        response = self.kitty_remote.raw("get-text", payload, want_response=True)
        if (
            isinstance(response, kitty_remote_api.KittyRcResponse)
            and response.ok
            and response.response_text is not None
        ):
            return ScreenReadResponse(succeeded=True, text=response.response_text)
        text = self.kitty_remote.read_text(screen_read_request.window_id, ansi=screen_read_request.ansi)
        if text is None:
            return ScreenReadResponse(succeeded=False, text=None, reason="terminal screen read failed")
        return ScreenReadResponse(succeeded=True, text=text)
