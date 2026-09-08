# Copyright (c) 2026 Zhambyl Yermagambet
"""Native automatic naming control tests."""

import os
import subprocess  # noqa: S404 -- Run local hook entries to check the internal-model guard.
import sys
import typing
from dataclasses import replace
from pathlib import Path

import pytest

from domain import (
    ids as domain_ids,
)
from harness import contract as harness_contract
from harness.impl.claude_code.plugin import plugin as claude_plugin
from harness.models import controls as control_models
from tests import (
    automatic_naming_models_two,
    automatic_naming_service_support,
    automatic_naming_session_helper,
    automatic_naming_values,
)


def test_claude_auto_name_stays_on_its_native() -> None:
    """Verify claude auto name stays on its native handler."""
    control_handler = automatic_naming_models_two.AcknowledgingHandler()
    plugin = replace(
        claude_plugin,
        controller=harness_contract.HarnessController(
            {
                control_models.ControlName.AUTO_NAME_SESSION: typing.cast(
                    "harness_contract.ControlHandler",
                    control_handler,
                ),
            },
        ),
    )
    stored_session = replace(automatic_naming_session_helper.session(), plugin=plugin)
    automatic_namer = automatic_naming_models_two.RecordingNamer()

    outcome = automatic_naming_service_support.control_service(
        stored_session, automatic_namer, automatic_naming_models_two.Effects(),
    ).auto_name_session(
        control_models.AutoNameSession(automatic_naming_values.SESSION_ID, domain_ids.RequestId("native")),
    )

    assert outcome.status == control_models.ControlAcknowledgement.ACKNOWLEDGED
    assert automatic_namer.calls == 0
    assert control_handler.requests == [
        control_models.AutoNameSession(automatic_naming_values.SESSION_ID, domain_ids.RequestId("native")),
    ]


@pytest.mark.parametrize("hook", ["codex_hook.py", "claude_hook.py"])
def test_internal_model_marker_suppresses_hook(
    hook: str,
) -> None:
    """Verify internal model marker suppresses hook delivery."""
    environment = os.environ.copy()
    environment["BAQYLAU_INTERNAL_MODEL"] = "1"
    environment["BAQYLAU_DASHBOARD_PORT"] = "1"
    hook_path = Path(__file__).resolve().parents[1] / "client" / hook
    command: list[str | Path] = [sys.executable, hook_path]

    completed = subprocess.run(  # noqa: S603 -- The test supplies one of two fixed local hook paths; no shell is used.
        command,
        input=b'{"session_id":"internal-model"}',
        capture_output=True,
        env=environment,
        timeout=5,
        check=False,
    )

    assert completed.returncode == 0
    assert completed.stdout == b""
