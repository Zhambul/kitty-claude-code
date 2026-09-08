# Copyright (c) 2026 Zhambyl Yermagambet
"""Own Codex control selections."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harness.contract import ControlHandler
from harness.impl.codex.controls import backtrack, modeldialog, modeldialog_steps
from harness.impl.codex.controls.controller_results import error_detail
from harness.impl.codex.controls.controller_values import SESSION_NOT_LIVE_REASON
from harness.models import controls as control_models
from harness.services.terminal_driver import TerminalDriver

if TYPE_CHECKING:
    from harness.impl.codex.continuity import RewindContinuity


class ApplyRewindHandler(ControlHandler):
    """Represent apply rewind handler."""

    def __init__(self, rewind_continuity: RewindContinuity) -> None:
        """Initialize the object."""
        self._rewind_continuity = rewind_continuity

    def __call__(
        self, request: control_models.ControlRequest, control_context: control_models.ControlContext,
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
        if request.mode != "conversation":
            return control_models.RewindResult(
                request.request_id,
                control_models.ControlAcknowledgement.REJECTED,
                "Codex supports conversation rewind only",
            )
        window_id = control_context.terminal_window_id
        if window_id is None:
            return control_models.RewindResult(
                request.request_id,
                control_models.ControlAcknowledgement.REJECTED,
                SESSION_NOT_LIVE_REASON,
            )
        try:
            backtrack.drive(
                TerminalDriver(control_context.terminal),
                window_id,
                request.target_text,
                newer_prompt_count=request.newer_prompt_count,
            )
        except backtrack.BacktrackError as error:
            return control_models.RewindResult(
                request.request_id,
                control_models.ControlAcknowledgement.INDETERMINATE,
                error_detail(error),
            )
        self._rewind_continuity.expect(request.session_id, window_id)
        return control_models.RewindResult(
            request.request_id,
            control_models.ControlAcknowledgement.ACKNOWLEDGED,
            restored_text=request.target_text,
        )


class SelectModelHandler(ControlHandler):
    """Represent select model handler."""

    def __call__(
        self, request: control_models.ControlRequest, control_context: control_models.ControlContext,
    ) -> control_models.ControlResult:
        """Handle a model-selection request.

        Returns:
            The control result.

        Raises:
            TypeError: If an input has an invalid type.

        """
        if not isinstance(request, control_models.SelectModel):
            msg = "select_model handler requires SelectModel"
            raise TypeError(msg)
        terminal = control_context.terminal
        window_id = control_context.terminal_window_id
        if window_id is None:
            return control_models.ControlResult(
                request.request_id, control_models.ControlAcknowledgement.REJECTED, SESSION_NOT_LIVE_REASON,
            )
        try:
            modeldialog.set_model_effort(
                TerminalDriver(terminal),
                window_id,
                model=request.model,
                effort=control_context.current_effort,
            )
        except modeldialog_steps.CodexModelError as error:
            return control_models.ControlResult(
                request.request_id, control_models.ControlAcknowledgement.INDETERMINATE, str(error),
            )
        return control_models.ControlResult(request.request_id, control_models.ControlAcknowledgement.ACKNOWLEDGED)


class SelectEffortHandler(ControlHandler):
    """Represent select effort handler."""

    def __call__(
        self, request: control_models.ControlRequest, control_context: control_models.ControlContext,
    ) -> control_models.ControlResult:
        """Handle an effort-selection request.

        Returns:
            The control result.

        Raises:
            TypeError: If an input has an invalid type.

        """
        if not isinstance(request, control_models.SelectEffort):
            msg = "select_effort handler requires SelectEffort"
            raise TypeError(msg)
        terminal = control_context.terminal
        window_id = control_context.terminal_window_id
        if window_id is None:
            return control_models.ControlResult(
                request.request_id, control_models.ControlAcknowledgement.REJECTED, SESSION_NOT_LIVE_REASON,
            )
        try:
            modeldialog.set_model_effort(
                TerminalDriver(terminal),
                window_id,
                effort=request.effort,
            )
        except modeldialog_steps.CodexModelError as error:
            return control_models.ControlResult(
                request.request_id, control_models.ControlAcknowledgement.INDETERMINATE, str(error),
            )
        return control_models.ControlResult(request.request_id, control_models.ControlAcknowledgement.ACKNOWLEDGED)
