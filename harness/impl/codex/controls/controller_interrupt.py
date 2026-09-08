# Copyright (c) 2026 Zhambyl Yermagambet
"""Own Codex control interrupt."""

from __future__ import annotations

from harness.contract import ControlHandler
from harness.impl.codex.controls.controller_interrupt_delivery import _deliver_interrupt
from harness.impl.codex.controls.controller_results import has_live_window
from harness.impl.codex.controls.controller_values import SESSION_NOT_LIVE_REASON
from harness.models import controls as control_models


class InterruptHandler(ControlHandler):
    """Represent interrupt handler."""

    def __call__(
        self,
        request: control_models.ControlRequest,
        control_context: control_models.ControlContext,
    ) -> control_models.InterruptResult:
        """Handle an interrupt request.

        Returns:
            The interrupt result.

        Raises:
            TypeError: If an input has an invalid type.

        """
        if not isinstance(request, control_models.Interrupt):
            msg = "interrupt handler requires Interrupt"
            raise TypeError(msg)
        window_id = control_context.terminal_window_id
        if not has_live_window(window_id):
            return control_models.InterruptResult(
                request.request_id, control_models.ControlAcknowledgement.REJECTED, SESSION_NOT_LIVE_REASON,
            )
        delivery = _deliver_interrupt(control_context, window_id)
        if delivery.corroborated:
            return control_models.InterruptResult(
                request.request_id,
                control_models.ControlAcknowledgement.ACKNOWLEDGED,
                corroborated=True,
            )
        return control_models.InterruptResult(
            request.request_id,
            control_models.ControlAcknowledgement.INDETERMINATE
            if delivery.delivered
            else control_models.ControlAcknowledgement.REJECTED,
            "turn_aborted was not observed" if delivery.delivered else "interrupt key was not delivered",
        )
