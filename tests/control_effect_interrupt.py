# Copyright (c) 2026 Zhambyl Yermagambet
"""Control effect interrupt."""

from __future__ import annotations

import threading
from dataclasses import dataclass
from functools import partial
from typing import TYPE_CHECKING

from harness.services import controls as control_services
from tests import control_effect_delivery as delivery, control_effect_interrupt_dependencies as interrupt_dependencies

if TYPE_CHECKING:
    import pytest


@dataclass(frozen=True)
class InterruptControlFixture:
    """Hold the control service and events used to coordinate an interrupt."""

    service: control_services.HarnessControlService
    send_started: threading.Event
    release_send: threading.Event
    interrupt_started: threading.Event


def interrupt_control_fixture(
    monkeypatch: pytest.MonkeyPatch,
) -> InterruptControlFixture:
    """Build a control service with coordinated send and interrupt requests.

    Returns:
        The service and its synchronization events.

    """
    service = control_services.HarnessControlService(
        interrupt_dependencies.interrupt_dependencies(),
    )
    send_started = threading.Event()
    release_send = threading.Event()
    interrupt_started = threading.Event()
    monkeypatch.setattr(
        service,
        "_audited",
        partial(
            delivery.coordinate_audited_control,
            send_started,
            release_send,
            interrupt_started,
        ),
    )
    return InterruptControlFixture(
        service,
        send_started,
        release_send,
        interrupt_started,
    )
