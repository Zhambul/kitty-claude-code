# Copyright (c) 2026 Zhambyl Yermagambet
"""Own Codex control compact."""

from __future__ import annotations

from harness.contract import ControlHandler
from harness.impl.codex.controls import composer
from harness.impl.codex.controls.controller_results import (
    error_detail,
    submit_text,
)
from harness.impl.codex.controls.controller_values import SESSION_NOT_LIVE_REASON
from harness.models import controls as control_models
from harness.services.terminal_driver import TerminalDriver


class CompactHandler(ControlHandler):
    """Represent compact handler."""

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
        window_id = control_context.terminal_window_id
        if window_id is None:
            return control_models.ControlResult(
                request.request_id,
                control_models.ControlAcknowledgement.REJECTED,
                SESSION_NOT_LIVE_REASON,
            )
        try:
            # A turn completion can reach the canonical feed just before the
            # TUI restores its prompt.  Verify the native composer is ready
            # before submitting the slash command; otherwise terminal input
            # can report successful delivery while Codex silently drops it.
            composer.clear(TerminalDriver(control_context.terminal), window_id)
        except composer.ComposerError as error:
            return control_models.ControlResult(
                request.request_id,
                control_models.ControlAcknowledgement.INDETERMINATE,
                error_detail(error),
            )
        return submit_text(request, control_context, "/compact")
