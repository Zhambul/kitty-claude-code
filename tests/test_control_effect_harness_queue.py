# Copyright (c) 2026 Zhambyl Yermagambet
"""Test control effect harness queue."""

from __future__ import annotations

from types import SimpleNamespace
from typing import TYPE_CHECKING, cast
from unittest.mock import Mock

import pytest

from harness.models import controls as control_models
from harness.services import controls as control_services

if TYPE_CHECKING:
    from audit.recorder import AuditRecorder
    from harness.services.control_effects import ControlEffectRecorder
    from repository.contract.sessions import SessionRepository

from tests import (
    control_effect_sessions as control_sessions,
    control_effect_stores as stores,
    control_effect_values as control_values,
)


@pytest.mark.parametrize(
    "status", [control_models.MessageDeliveryStatus.QUEUED, control_models.MessageDeliveryStatus.SENT],
)
def test_only_harness_queued_message_is_recorded(
    monkeypatch: pytest.MonkeyPatch,
    status: control_models.MessageDeliveryStatus,
) -> None:
    """Verify only a harness queued message is recorded."""
    recorded = []
    session = control_sessions.codex_session()
    service = control_services.HarnessControlService(Mock())
    service.audit = cast(
        "AuditRecorder",
        SimpleNamespace(state_file=lambda *_args, **_kwargs: None),
    )
    service.control_effects = cast(
        "ControlEffectRecorder",
        SimpleNamespace(
            message_queued=lambda found, request: recorded.append(
                ("queued", found, request),
            ),
        ),
    )
    service.sessions = cast("SessionRepository", stores.Sessions(session))
    monkeypatch.setattr(
        service,
        "_execute",
        lambda request: control_models.MessageDeliveryResult(request.request_id, status),
    )
    request = control_models.SendText(
        control_values.TEST_SESSION_ID,
        control_values.TEST_REQUEST_ID,
        text=control_values.NEXT_PROMPT,
    )

    service.send_text(request)

    expected_records = [("queued", session, request)] if status == "queued" else []
    assert recorded == expected_records
