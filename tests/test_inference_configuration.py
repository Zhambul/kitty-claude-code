# Copyright (c) 2026 Zhambyl Yermagambet
"""Inference executable configuration tests."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from inference import (
    commands as inference_commands,
    contract as inference_contract,
    default as inference_default,
    options as inference_options,
)
from terminal.models import tabs
from tests.inference_support import Audit, InferenceTerminal, Usage

if TYPE_CHECKING:
    from audit.recorder import AuditRecorder

MODEL_PROMPT = "name this"
TEST_SESSION_ID = "session-one"


def test_configured_executable_does_not_depend() -> None:
    """Verify configured executable does not depend on the daemon path."""
    terminal = InferenceTerminal(('{"title":"Configured executable session title"}',))
    model_factory = inference_default.DefaultModelFactory(
        terminal.plugin(),
        Usage(),
        cast("AuditRecorder", Audit()),
        inference_options.DefaultModelOptions(
            executable_resolver=lambda name: "/private/model-bin/codex" if name == "codex" else None,
        ),
    )
    response = model_factory.small().send(inference_contract.ModelPromptRequest(MODEL_PROMPT))
    assert response.text == "Configured executable session title"
    launch = terminal.opened_tabs[0]
    assert launch.command[0] == "/private/model-bin/codex"
    assert launch.environment[0] == tabs.EnvironmentVariable(inference_commands.INTERNAL_MODEL_VARIABLE, "1")
    assert launch.environment[1].name == "CODEX_HOME"
