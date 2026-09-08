# Copyright (c) 2026 Zhambyl Yermagambet
"""Own Claude Code text delivery."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harness.contract import ControlHandler
from harness.impl.claude_code import attachments as claude_attachments
from harness.impl.claude_code.controls import (
    controller_send_operations as operations,
    controller_values as control_values,
)
from harness.impl.claude_code.controls.controller_commands import has_live_window
from harness.impl.claude_code.probe import ClaudeCodeComposer
from harness.models import controls as control_models
from harness.services.terminal_driver import TerminalDriver

if TYPE_CHECKING:
    from domain.ids import WindowId


def _wait_for_native_text_state(source_reference: str, after_position: int, expected: str) -> str | None:
    deadline = operations.time.monotonic() + control_values.NATIVE_TEXT_CONFIRM_TIMEOUT_SECONDS
    while True:
        state = operations.native_text_state(source_reference, after_position, expected)
        if state is not None:
            return state
        if operations.time.monotonic() >= deadline:
            return None
        operations.time.sleep(control_values.NATIVE_TEXT_CONFIRM_POLL_SECONDS)


def deliver_native_text(
    control_context: control_models.ControlContext,
    terminal_driver: TerminalDriver,
    window_id: WindowId,
    message: str,
    *,
    ensure_submit: bool = False,
) -> tuple[str | None, str | None]:
    """Submit text and require a native acknowledgement.

    Returns:
        The native state and an optional failure reason.

    """
    source_reference = control_context.session.source_reference
    try:
        transcript_position = operations.pathlib.Path(source_reference).stat().st_size
    except FileNotFoundError:
        # A session launched without a prompt creates its transcript on send.
        transcript_position = 0
    except OSError:
        return None, "Claude Code transcript could not be read"
    for _ in range(control_values.NATIVE_TEXT_DELIVERY_ATTEMPTS):
        native_state = operations.native_text_state(source_reference, transcript_position, message)
        if native_state is not None:
            return native_state, None
        if not _type_native_text(terminal_driver, window_id, message, ensure_submit=ensure_submit):
            return None, "terminal message was not delivered"
        native_state = _wait_for_native_text_state(source_reference, transcript_position, message)
        if native_state is not None:
            return native_state, None
    return None, "Claude Code did not confirm the message"


def _type_native_text(
    terminal_driver: TerminalDriver,
    window_id: WindowId,
    message: str,
    *,
    ensure_submit: bool,
) -> bool:
    return operations.tui.type_command(
        terminal_driver,
        window_id,
        message,
        ensure_submit=ensure_submit,
    )[0]


class SendTextHandler(ControlHandler):
    """Send text to Claude Code."""

    def __call__(
        self,
        request: control_models.ControlRequest,
        control_context: control_models.ControlContext,
    ) -> control_models.ControlResult | control_models.MessageDeliveryResult:
        """Handle a send-text request.

        Returns:
            The delivery result.

        Raises:
            TypeError: If an input has an invalid type.

        """
        if not isinstance(request, control_models.SendText):
            msg = "send_text handler requires SendText"
            raise TypeError(msg)
        window_id = control_context.terminal_window_id
        if not has_live_window(window_id):
            return control_models.ControlResult(
                request.request_id,
                control_models.ControlAcknowledgement.REJECTED,
                control_values.SESSION_NOT_LIVE_REASON,
            )
        driver = TerminalDriver(control_context.terminal)
        return _send_text_result(request, control_context, driver, window_id)


def _send_text_result(
    request: control_models.SendText,
    control_context: control_models.ControlContext,
    terminal_driver: TerminalDriver,
    window_id: WindowId,
) -> control_models.ControlResult | control_models.MessageDeliveryResult:
    try:
        ClaudeCodeComposer().clear(terminal_driver, window_id)
    except Exception as error:  # noqa: BLE001 — the raised-path assertion
        return control_models.ControlResult(
            request.request_id,
            control_models.ControlAcknowledgement.REJECTED,
            str(error),
        )
    message = claude_attachments.control_prompt_with_attachments(request.text, request.attachments)
    native_state, reason = deliver_native_text(
        control_context,
        terminal_driver,
        window_id,
        message,
        ensure_submit=bool(request.attachments),
    )
    if native_state is not None:
        delivery_status = (
            control_models.MessageDeliveryStatus.QUEUED
            if native_state == control_values.NATIVE_TEXT_QUEUED
            else control_models.MessageDeliveryStatus.SENT
        )
        return control_models.MessageDeliveryResult(request.request_id, delivery_status)
    return control_models.ControlResult(
        request.request_id,
        control_models.ControlAcknowledgement.REJECTED,
        reason,
    )
