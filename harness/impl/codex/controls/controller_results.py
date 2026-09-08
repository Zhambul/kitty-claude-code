# Copyright (c) 2026 Zhambyl Yermagambet
"""Own Codex control results."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, TypeGuard

from harness.impl.codex.controls.controller_values import SESSION_NOT_LIVE_REASON
from harness.models import controls as control_models
from terminal.models.input import (
    TextInputMode,
    TextSubmitRequest,
)
from terminal.models.values import WindowId as NativeWindowId

if TYPE_CHECKING:
    from domain.ids import WindowId


def has_live_window(window_id: WindowId | None) -> TypeGuard[WindowId]:
    """Return whether a terminal window is available.

    Returns:
        True if a terminal window is available; otherwise, false.

    """
    return window_id is not None


@dataclass(frozen=True)
class RolloutPosition:
    """Represent rollout position."""

    path: str
    position: int


def control_result(
    request: control_models.ControlRequest, *, succeeded: bool, reason: str,
) -> control_models.ControlResult:
    """Build the result for a terminal action.

    Returns:
        An acknowledged result on success, or an indeterminate result with the reason.

    """
    return control_models.ControlResult(
        request.request_id,
        control_models.ControlAcknowledgement.ACKNOWLEDGED
        if succeeded
        else control_models.ControlAcknowledgement.INDETERMINATE,
        None if succeeded else reason,
    )


def session_not_live(request: control_models.ControlRequest) -> control_models.ControlResult:
    """Return the result for a control without a terminal window.

    Returns:
        The rejected control result.

    """
    return control_models.ControlResult(
        request.request_id,
        control_models.ControlAcknowledgement.REJECTED,
        SESSION_NOT_LIVE_REASON,
    )


def error_detail(failure: Exception) -> str:
    """Return the text from one native control failure.

    Returns:
        The failure text.

    """
    return str(failure)


def submit_text(
    request: control_models.ControlRequest, control_context: control_models.ControlContext, text: str,
) -> control_models.ControlResult:
    """Submit text to the session terminal.

    Returns:
        The delivery result, or a rejected result if no window is available.

    """
    window_id = control_context.terminal_window_id
    if not has_live_window(window_id):
        return session_not_live(request)
    result = control_context.terminal.input.submit_text(
        TextSubmitRequest(NativeWindowId(str(window_id)), text, TextInputMode.PASTE),
    )
    return control_result(
        request,
        succeeded=result.succeeded,
        reason=result.reason or "terminal text was not delivered",
    )


def message_text(send_text: control_models.SendText) -> str:
    """Join attachment paths and prompt text for terminal submission.

    Returns:
        The attachment paths followed by the prompt, with a newline between them.

    """
    attachments = " ".join(attachment.local_path for attachment in send_text.attachments)
    separator = "\n" if attachments and send_text.text else ""
    return attachments + separator + send_text.text
