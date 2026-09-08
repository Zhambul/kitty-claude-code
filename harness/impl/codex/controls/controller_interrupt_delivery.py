# Copyright (c) 2026 Zhambyl Yermagambet
"""Own Codex control interrupt delivery."""

from __future__ import annotations

import pathlib
import time
from dataclasses import dataclass
from typing import TYPE_CHECKING

from harness.impl.codex.controls.controller_rollout import rollout_abort_state
from harness.impl.codex.controls.controller_timeouts import INTERRUPT_CONFIRMATION_TIMEOUT_SECONDS
from terminal.models.input import (
    KeySendRequest,
)
from terminal.models.values import WindowId as NativeWindowId

if TYPE_CHECKING:
    from domain.ids import WindowId
    from harness.models import controls as control_models


@dataclass(frozen=True)
class _InterruptDelivery:
    delivered: bool
    corroborated: bool


def _deliver_interrupt(control_context: control_models.ControlContext, window_id: WindowId) -> _InterruptDelivery:
    source_reference = control_context.session.source_reference
    position = _source_position(source_reference)
    delivered = False
    native_window_id = NativeWindowId(str(window_id))
    for _ in range(2):
        delivered = _interrupt_key_delivered(control_context, native_window_id) or delivered
        if not delivered:
            break
        if _interrupt_corroborated(source_reference, position):
            return _InterruptDelivery(delivered=True, corroborated=True)
    return _InterruptDelivery(delivered=delivered, corroborated=False)


def _interrupt_key_delivered(control_context: control_models.ControlContext, window_id: NativeWindowId) -> bool:
    return control_context.terminal.input.send_key(KeySendRequest(window_id, "escape")).succeeded


def _source_position(source_reference: str) -> int:
    try:
        return pathlib.Path(source_reference).stat().st_size
    except OSError:
        return -1


def _interrupt_corroborated(source_reference: str, position: int) -> bool:
    deadline = time.monotonic() + INTERRUPT_CONFIRMATION_TIMEOUT_SECONDS
    while time.monotonic() < deadline:
        time.sleep(0.1)
        if position >= 0 and rollout_abort_state(source_reference, position)[0]:
            return True
    return False
