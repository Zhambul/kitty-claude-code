# Copyright (c) 2026 Zhambyl Yermagambet
"""Test control effect durable title."""

from __future__ import annotations

from types import SimpleNamespace
from typing import TYPE_CHECKING, cast
from unittest.mock import Mock

from harness.models import controls as control_models
from harness.models.session import (
    Session,
)
from harness.services import controls as control_services

if TYPE_CHECKING:
    import pytest

    from audit.recorder import AuditRecorder
    from harness.services.control_effects import ControlEffectRecorder
    from repository.contract.sessions import SessionRepository

from tests import control_effect_stores as stores, control_effect_values as control_values


def test_only_confirmed_durable_rename(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify only a confirmed durable rename is recorded."""
    session = Session(
        control_values.TEST_SESSION_ID,
        control_values.TEST_ACTOR_ID,
        control_values.ROLLOUT_SOURCE_NAME,
        control_values.TEST_WORKING_DIRECTORY,
    )
    recorded = []
    service = control_services.HarnessControlService(Mock())
    service.audit = cast(
        "AuditRecorder",
        SimpleNamespace(state_file=lambda *_args, **_kwargs: None),
    )
    service.sessions = cast("SessionRepository", stores.Sessions(session))
    service.control_effects = cast(
        "ControlEffectRecorder",
        SimpleNamespace(
            session_renamed=lambda found, request: recorded.append((found, request)),
        ),
    )
    request = control_models.RenameSession(
        session.session_id,
        control_values.TEST_REQUEST_ID,
        "Parked title",
    )
    monkeypatch.setattr(
        service,
        "_execute",
        lambda _request: control_models.DurableTitleResult(
            request.request_id,
            control_models.ControlAcknowledgement.ACKNOWLEDGED,
        ),
    )

    service.rename_session(request)

    assert recorded == [(session, request)]
