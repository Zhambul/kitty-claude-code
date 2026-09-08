# Copyright (c) 2026 Zhambyl Yermagambet
"""Own Codex control close session."""

from __future__ import annotations

from harness.contract import ControlHandler
from harness.impl.codex.controls.controller_interrupt import InterruptHandler
from harness.impl.codex.controls.controller_results import (
    control_result,
    has_live_window,
    session_not_live,
)
from harness.models import controls as control_models
from terminal.models.tabs import (
    TabCloseRequest,
)
from terminal.models.values import WindowId as NativeWindowId


class CloseSessionHandler(ControlHandler):
    """Represent close session handler."""

    def __call__(
        self, request: control_models.ControlRequest, control_context: control_models.ControlContext,
    ) -> control_models.ControlResult:
        """Handle a session-close request.

        Returns:
            The control result.

        Raises:
            TypeError: If an input has an invalid type.

        """
        terminal = control_context.terminal
        if not isinstance(request, control_models.CloseSession):
            msg = "close_session handler requires CloseSession"
            raise TypeError(msg)
        window_id = control_context.terminal_window_id
        if not has_live_window(window_id):
            return session_not_live(request)
        if control_context.lead_active:
            InterruptHandler()(
                control_models.Interrupt(request.session_id, request.request_id),
                control_context,
            )
        result = terminal.tabs.close_tab(TabCloseRequest(NativeWindowId(str(window_id))))
        if not result.succeeded:
            return control_result(
                request,
                succeeded=False,
                reason=result.reason or "terminal tab was not closed",
            )
        return control_result(
            request,
            succeeded=True,
            reason="terminal tab was not closed",
        )
