# Copyright (c) 2026 Zhambyl Yermagambet
"""Expose a recorded prompt without waiting for another source scan."""

from __future__ import annotations

from http import HTTPStatus
from threading import Event
from unittest.mock import Mock

import pytest

from core.work_queue import WorkKind
from domain.ids import HarnessName
from engine.worker import EngineWorker
from tests import http_test_assets, http_test_controls
from tests.plugin_tests.support_events import raw_event
from tests.provider_graph import ProviderGraph


@pytest.mark.parametrize("harness", [HarnessName.CODEX, HarnessName.CLAUDE_CODE])
def test_prompt_reaches_http_in_one_pass(harness: HarnessName, monkeypatch: pytest.MonkeyPatch) -> None:
    """Translate and display either harness's prompt in the same worker pass."""
    application = ProviderGraph()
    native: http_test_controls.JsonValue = (
        {"type": "response_item", "payload": {"type": "message", "role": "user", "content": "Send marker"}}
        if harness == HarnessName.CODEX
        else {"type": "user", "uuid": "send-marker", "message": {"role": "user", "content": "Send marker"}}
    )
    application.raw_events.record((raw_event(
        native,
        harness=harness,
        source_type="rollout" if harness == HarnessName.CODEX else "transcript",
        raw_event_id="send-marker",
    ),))
    worker = application.provider("engine_worker", EngineWorker)
    worker.inputs = Mock()
    monkeypatch.setattr(
        worker.work_queue, "take",
        Mock(side_effect=[{WorkKind.RAW}, set()]),
    )
    worker.run(Event())
    with http_test_assets.running_server(application) as server:
        response = http_test_controls.get(server, "/sessionData/session-one/entries")
        assert response.status == HTTPStatus.OK
        assert "Send marker" in response.body.raw.decode()
