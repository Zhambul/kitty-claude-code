# Copyright (c) 2026 Zhambyl Yermagambet
"""Control effect delivery."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harness.models import controls as control_models

if TYPE_CHECKING:
    import threading


def coordinate_audited_control(
    send_started: threading.Event,
    release_send: threading.Event,
    interrupt_started: threading.Event,
    request: control_models.ControlRequest,
) -> control_models.ControlResult | control_models.MessageDeliveryResult:
    """Hold message delivery until released and signal other control requests.

    Returns:
        A queued message result or a control acknowledgement.

    """
    if isinstance(request, control_models.SendText):
        send_started.set()
        assert release_send.wait(1)
        return control_models.MessageDeliveryResult(
            request.request_id,
            control_models.MessageDeliveryStatus.QUEUED,
        )
    interrupt_started.set()
    return control_models.ControlResult(
        request.request_id,
        control_models.ControlAcknowledgement.ACKNOWLEDGED,
    )
