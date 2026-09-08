# Copyright (c) 2026 Zhambyl Yermagambet
"""Move a Claude Code command to the background."""

from __future__ import annotations

import re
import time
from typing import TYPE_CHECKING

from harness.contract import ControlHandler
from harness.models import controls as control_models
from terminal.models.input import KeySendRequest
from terminal.models.values import WindowId as NativeWindowId
from terminal.models.viewport import ScreenReadRequest

if TYPE_CHECKING:
    from domain.ids import WindowId
    from terminal.contract import TerminalPlugin

BACKGROUND_OFFER_MARKER = "runinbackground"
BACKGROUND_CHORD = "ctrl+b"
BACKGROUND_OFFER_TIMEOUT_SECONDS = 15.0
BACKGROUND_POLL_SECONDS = 0.2
SESSION_NOT_LIVE_REASON = "session is not live"
WHITESPACE = re.compile(r"\s+")


def _screen_text(terminal_plugin: TerminalPlugin, window_id: WindowId) -> str | None:
    request = ScreenReadRequest(NativeWindowId(str(window_id)))
    return terminal_plugin.viewport.read_screen(request).text


def _send_background_key(terminal_plugin: TerminalPlugin, window_id: WindowId) -> bool:
    request = KeySendRequest(NativeWindowId(str(window_id)), BACKGROUND_CHORD)
    return terminal_plugin.input.send_key(request).succeeded


def _flattened(screen: str | None) -> str:
    return WHITESPACE.sub("", (screen or "").lower())


class BackgroundHandler(ControlHandler):
    """Move a running command after Claude Code offers the action."""

    def __call__(
        self,
        request: control_models.ControlRequest,
        control_context: control_models.ControlContext,
    ) -> control_models.ControlResult:
        """Handle a background request.

        Returns:
            The control result.

        Raises:
            TypeError: If an input has an invalid type.

        """
        if not isinstance(request, control_models.Background):
            msg = "background handler requires Background"
            raise TypeError(msg)
        window_id = control_context.terminal_window_id
        if window_id is None:
            return control_models.ControlResult(
                request.request_id,
                control_models.ControlAcknowledgement.REJECTED,
                SESSION_NOT_LIVE_REASON,
            )
        terminal = control_context.terminal
        deadline = time.monotonic() + BACKGROUND_OFFER_TIMEOUT_SECONDS
        while BACKGROUND_OFFER_MARKER not in _flattened(_screen_text(terminal, window_id)):
            if time.monotonic() >= deadline:
                return control_models.ControlResult(
                    request.request_id,
                    control_models.ControlAcknowledgement.REJECTED,
                    "no command is offering to be backgrounded",
                )
            time.sleep(BACKGROUND_POLL_SECONDS)
        delivered = _send_background_key(terminal, window_id)
        return control_models.ControlResult(
            request.request_id,
            control_models.ControlAcknowledgement.ACKNOWLEDGED
            if delivered
            else control_models.ControlAcknowledgement.INDETERMINATE,
            None if delivered else "backgrounding chord was not delivered",
        )
