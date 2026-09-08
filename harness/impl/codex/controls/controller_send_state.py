# Copyright (c) 2026 Zhambyl Yermagambet
"""Own Codex control send state."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from harness.impl.codex.controls import composer
from harness.impl.codex.controls.controller_results import (
    RolloutPosition,
    control_result,
    error_detail,
    message_text,
    submit_text,
)
from harness.models import controls as control_models
from harness.services.terminal_driver import TerminalDriver

if TYPE_CHECKING:
    from domain.ids import WindowId


@dataclass(frozen=True)
class SendState:
    """Keep the terminal and source state for one text submission."""

    driver: TerminalDriver
    rewind_pending: bool
    source_positions: tuple[RolloutPosition, ...]
    submitted_message: str
    expected_message: str


def queue_active_message(
    request: control_models.SendText,
    control_context: control_models.ControlContext,
) -> control_models.ControlResult | control_models.MessageDeliveryResult:
    """Submit a message while the session is active.

    Returns:
        A queued delivery result on success, or a rejected control result.

    """
    submission = submit_text(request, control_context, message_text(request))
    if submission.status != control_models.ControlAcknowledgement.ACKNOWLEDGED:
        return control_models.ControlResult(
            submission.request_id, control_models.ControlAcknowledgement.REJECTED, submission.reason,
        )
    return control_models.MessageDeliveryResult(submission.request_id, control_models.MessageDeliveryStatus.QUEUED)


def clear_composer(terminal_driver: TerminalDriver, window_id: WindowId) -> str | None:
    """Clear the native composer.

    Returns:
        The failure reason, or None on success.

    """
    try:
        composer.clear(terminal_driver, window_id)
    except composer.ComposerError as error:
        return str(error)
    return None


def submit_message(
    request: control_models.SendText,
    control_context: control_models.ControlContext,
    window_id: WindowId,
    send_state: SendState,
) -> control_models.ControlResult:
    """Submit a message with the required rewind handling.

    Returns:
        The terminal delivery result.

    """
    if not send_state.rewind_pending:
        return submit_text(request, control_context, send_state.submitted_message)
    try:
        composer.CodexComposer().insert(
            send_state.driver,
            window_id,
            send_state.submitted_message,
        )
    except composer.ComposerError as error:
        return control_models.ControlResult(
            request.request_id, control_models.ControlAcknowledgement.REJECTED, error_detail(error),
        )
    return control_result(
        request,
        succeeded=send_state.driver.send_key(window_id, "enter"),
        reason="the Codex message enter key was not delivered",
    )
