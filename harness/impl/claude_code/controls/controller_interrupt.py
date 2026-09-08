# Copyright (c) 2026 Zhambyl Yermagambet
"""Own Claude Code interrupt delivery."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from harness.contract import ControlHandler
from harness.impl.claude_code.controls.controller_interrupt_records import (
    _interrupt_corroborated,
    _transcript_position,
)
from harness.impl.claude_code.probe import ClaudeCodeComposer
from harness.models import controls as control_models
from harness.services.terminal_driver import TerminalDriver
from terminal.models.input import KeySendRequest
from terminal.models.values import WindowId as NativeWindowId

if TYPE_CHECKING:
    from domain.ids import WindowId

SESSION_NOT_LIVE_REASON = "session is not live"


@dataclass(frozen=True)
class _InterruptDelivery:
    delivered: bool
    corroborated: bool


def _deliver_interrupt(control_context: control_models.ControlContext, window_id: WindowId) -> _InterruptDelivery:
    position = _transcript_position(control_context.session.source_reference)
    delivered = False
    native_window_id = NativeWindowId(str(window_id))
    for _ in range(2):
        sent = control_context.terminal.input.send_key(KeySendRequest(native_window_id, "escape")).succeeded
        delivered = delivered or sent
        if not delivered:
            break
        if _interrupt_corroborated(control_context.session.source_reference, position):
            return _InterruptDelivery(delivered=True, corroborated=True)
    return _InterruptDelivery(delivered=delivered, corroborated=False)


class InterruptHandler(ControlHandler):
    """Interrupt an active Claude Code turn."""

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
        if window_id is None:
            return control_models.InterruptResult(
                request.request_id,
                control_models.ControlAcknowledgement.REJECTED,
                SESSION_NOT_LIVE_REASON,
            )
        delivery = _deliver_interrupt(control_context, window_id)
        input_state = ClaudeCodeComposer().read(TerminalDriver(control_context.terminal), window_id)
        restored_text = input_state.typed_text if input_state and input_state.typed_text else ""
        if delivery.corroborated:
            return control_models.InterruptResult(
                request.request_id,
                control_models.ControlAcknowledgement.ACKNOWLEDGED,
                restored_text=restored_text,
                corroborated=True,
            )
        return control_models.InterruptResult(
            request.request_id,
            control_models.ControlAcknowledgement.INDETERMINATE
            if delivery.delivered
            else control_models.ControlAcknowledgement.REJECTED,
            "native interrupt marker was not observed" if delivery.delivered else "interrupt key was not delivered",
            restored_text=restored_text,
        )
