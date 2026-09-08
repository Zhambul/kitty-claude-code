# Copyright (c) 2026 Zhambyl Yermagambet
"""Own Claude Code command controls."""

from __future__ import annotations

from typing import TYPE_CHECKING, TypeGuard

from harness.contract import ControlHandler
from harness.impl.claude_code.controls import confirmdialog, controller_values as control_values, tui
from harness.models import controls as control_models
from harness.services.terminal_driver import TerminalDriver

if TYPE_CHECKING:
    from domain.ids import WindowId


def has_live_window(window_id: WindowId | None) -> TypeGuard[WindowId]:
    """Check whether the control context has a terminal window.

    Returns:
        True if the window identifier is present.

    """
    return window_id is not None


def control_result(
    request: control_models.ControlRequest,
    *,
    succeeded: bool,
    reason: str,
) -> control_models.ControlResult:
    """Build the result for a terminal action.

    Returns:
        An acknowledged result on success, or the failure reason.

    """
    return control_models.ControlResult(
        request.request_id,
        control_models.ControlAcknowledgement.ACKNOWLEDGED
        if succeeded
        else control_models.ControlAcknowledgement.INDETERMINATE,
        None if succeeded else reason,
    )


def send_command(
    request: control_models.ControlRequest,
    control_context: control_models.ControlContext,
    text: str,
    *,
    confirm: bool = False,
) -> control_models.ControlResult:
    """Send a command and check its confirmation when requested.

    Returns:
        The delivery and confirmation result, or a failure reason.

    """
    window_id = control_context.terminal_window_id
    if not has_live_window(window_id):
        return control_models.ControlResult(
            request.request_id,
            control_models.ControlAcknowledgement.REJECTED,
            control_values.SESSION_NOT_LIVE_REASON,
        )
    driver = TerminalDriver(control_context.terminal)
    succeeded, _cleared_image = tui.type_command(driver, window_id, text)
    if not succeeded:
        return control_result(request, succeeded=False, reason="terminal command was not delivered")
    if not confirm:
        return control_models.CommandResult(request.request_id, control_models.ControlAcknowledgement.ACKNOWLEDGED)
    try:
        confirmation = confirmdialog.confirm(driver, window_id)
    except confirmdialog.ConfirmError as error:
        return control_models.CommandResult(
            request.request_id,
            control_models.ControlAcknowledgement.INDETERMINATE,
            reason=str(error),
            confirmation=control_models.ConfirmationOutcome.FAILED,
        )
    return control_models.CommandResult(
        request.request_id,
        control_models.ControlAcknowledgement.ACKNOWLEDGED,
        confirmation=(
            control_models.ConfirmationOutcome.CONFIRMED
            if confirmation.dialog
            else control_models.ConfirmationOutcome.NOT_NEEDED
        ),
    )


class OpenRewindHandler(ControlHandler):
    """Open the rewind menu."""

    def __call__(
        self, request: control_models.ControlRequest, control_context: control_models.ControlContext,
    ) -> control_models.ControlResult:
        """Handle an open-rewind request.

        Returns:
            The control result.

        Raises:
            TypeError: If an input has an invalid type.

        """
        if not isinstance(request, control_models.OpenRewind):
            msg = "open_rewind handler requires OpenRewind"
            raise TypeError(msg)
        return send_command(request, control_context, "/rewind")


class CompactHandler(ControlHandler):
    """Compact a Claude Code session."""

    def __call__(
        self, request: control_models.ControlRequest, control_context: control_models.ControlContext,
    ) -> control_models.ControlResult:
        """Handle a compact request.

        Returns:
            The control result.

        Raises:
            TypeError: If an input has an invalid type.

        """
        if not isinstance(request, control_models.Compact):
            msg = "compact handler requires Compact"
            raise TypeError(msg)
        return send_command(request, control_context, "/compact")


class SelectModelHandler(ControlHandler):
    """Select a Claude Code model."""

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
        return send_command(request, control_context, f"/model {request.model}", confirm=True)


class SelectEffortHandler(ControlHandler):
    """Select Claude Code effort."""

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
        return send_command(request, control_context, f"/effort {request.effort}", confirm=True)
