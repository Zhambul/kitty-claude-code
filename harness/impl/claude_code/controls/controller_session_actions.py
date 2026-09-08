# Copyright (c) 2026 Zhambyl Yermagambet
"""Own Claude Code session actions."""

from harness.contract import ControlHandler
from harness.impl.claude_code.controls import rewindmenu, screen_driver as screen_drive
from harness.impl.claude_code.controls.controller_commands import control_result
from harness.impl.claude_code.controls.controller_interrupt import InterruptHandler
from harness.impl.claude_code.controls.controller_values import SESSION_NOT_LIVE_REASON
from harness.impl.claude_code.controls.rewind_models import MenuError, RewindRequest
from harness.models import controls as control_models
from harness.services.terminal_driver import TerminalDriver
from terminal.models.tabs import TabCloseRequest
from terminal.models.values import WindowId as NativeWindowId


class CloseSessionHandler(ControlHandler):
    """Close a Claude Code session."""

    def __call__(
        self,
        request: control_models.ControlRequest,
        control_context: control_models.ControlContext,
    ) -> control_models.ControlResult:
        """Handle a session-close request.

        Returns:
            The control result.

        Raises:
            TypeError: If an input has an invalid type.

        """
        if not isinstance(request, control_models.CloseSession):
            msg = "close_session handler requires CloseSession"
            raise TypeError(msg)
        window_id = control_context.terminal_window_id
        if window_id is None:
            return control_models.ControlResult(
                request.request_id,
                control_models.ControlAcknowledgement.REJECTED,
                SESSION_NOT_LIVE_REASON,
            )
        if control_context.lead_active:
            InterruptHandler()(
                control_models.Interrupt(request.session_id, request.request_id),
                control_context,
            )
        result = control_context.terminal.tabs.close_tab(TabCloseRequest(NativeWindowId(str(window_id))))
        if not result.succeeded:
            return control_result(
                request,
                succeeded=False,
                reason=result.reason or "terminal tab was not closed",
            )
        return control_result(request, succeeded=True, reason="terminal tab was not closed")


class ApplyRewindHandler(ControlHandler):
    """Apply a Claude Code rewind choice."""

    def __call__(
        self,
        request: control_models.ControlRequest,
        control_context: control_models.ControlContext,
    ) -> control_models.RewindResult:
        """Handle an apply-rewind request.

        Returns:
            The rewind result.

        Raises:
            TypeError: If an input has an invalid type.

        """
        if not isinstance(request, control_models.ApplyRewind):
            msg = "apply_rewind handler requires ApplyRewind"
            raise TypeError(msg)
        window_id = control_context.terminal_window_id
        if window_id is None:
            return control_models.RewindResult(
                request.request_id,
                control_models.ControlAcknowledgement.REJECTED,
                SESSION_NOT_LIVE_REASON,
            )
        try:
            result = rewindmenu.drive(
                TerminalDriver(control_context.terminal),
                window_id,
                RewindRequest(request.target_text, request.mode, request.newer_prompt_count + 1),
            )
        except MenuError as error:
            return control_models.RewindResult(
                request.request_id,
                control_models.ControlAcknowledgement.INDETERMINATE,
                screen_drive.failure_detail(error),
            )
        restored = request.target_text if request.mode in {"conversation", "both"} else ""
        return control_models.RewindResult(
            request.request_id,
            control_models.ControlAcknowledgement.ACKNOWLEDGED,
            restored_text=restored,
            degraded=result.degraded,
        )
