# Copyright (c) 2026 Zhambyl Yermagambet
"""Test control effect interrupt."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from typing import TYPE_CHECKING

from domain import ids as domain_ids
from harness.models import controls as control_models
from tests import control_effect_interrupt as interrupt, control_effect_values as control_values

if TYPE_CHECKING:
    import pytest


def test_interrupt_waits_for_active_message(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify an interrupt waits for an active message delivery."""
    control_fixture = interrupt.interrupt_control_fixture(monkeypatch)

    with ThreadPoolExecutor(max_workers=2) as workers:
        send_result = workers.submit(
            control_fixture.service.send_text,
            control_models.SendText(
                control_values.TEST_SESSION_ID,
                domain_ids.RequestId("send-one"),
                text="queue this",
            ),
        )
        assert control_fixture.send_started.wait(1)
        interrupt_result = workers.submit(
            control_fixture.service.interrupt,
            control_models.Interrupt(
                control_values.TEST_SESSION_ID,
                domain_ids.RequestId("interrupt-one"),
            ),
        )
        assert not control_fixture.interrupt_started.wait(0.1)
        control_fixture.release_send.set()

        assert send_result.result().status == control_models.MessageDeliveryStatus.QUEUED
        assert interrupt_result.result().status == control_models.ControlAcknowledgement.ACKNOWLEDGED
        assert control_fixture.interrupt_started.is_set()
