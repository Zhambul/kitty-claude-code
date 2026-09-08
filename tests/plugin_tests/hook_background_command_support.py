# Copyright (c) 2026 Zhambyl Yermagambet
"""Support for background command tests."""

import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

import pytest

from engine.interpret.loop import Interpreter
from harness.impl.claude_code.hooks import gateway as claude_hooks
from tests.canonical_runtime import CanonicalRuntime
from tests.plugin_tests import support_hooks, support_runtime, vocabulary as fixture
from tests.plugin_tests.hook_background_support import (
    BackgroundHookFixture,
    foreground_background_hook,
    register_background_session,
    start_foreground_following,
)
from tests.plugin_tests.hook_common_support import tick_interpreter


@dataclass(frozen=True)
class BackgroundCommandFixture:
    """Hold a command's runtime, interpreter, output path, and starting hook."""

    runtime: CanonicalRuntime
    interpreter: Interpreter
    tee_path: Path
    hook: BackgroundHookFixture


def background_command_fixture(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> BackgroundCommandFixture:
    """Start a command output subscription and write its first output.

    Returns:
        The runtime, interpreter, output path, and original hook fixture.

    """
    monkeypatch.setenv(fixture.BAQYLAU_DATA_DIR_ENV, str(tmp_path / fixture.DATA_FIELD))
    hook = foreground_background_hook(tmp_path)
    runtime, interpreter = support_runtime.interpreting_runtime(
        tmp_path / fixture.DATA_FIELD / fixture.MAIN_DB_PATH,
    )
    register_background_session(runtime, fixture.SESSION_ONE_ID, hook.transcript_path)
    tee_path = start_foreground_following(runtime, interpreter, fixture.SESSION_ONE_ID)
    tee_path.write_bytes(b"working\n")
    tick_interpreter(interpreter, 2)
    return BackgroundCommandFixture(runtime, interpreter, tee_path, hook)


def deliver_backgrounded_hook(gateway: claude_hooks.ClaudeHookGateway, hook: Mapping[str, object]) -> None:
    """Deliver the post-tool hook that backgrounds a command."""
    backgrounded_hook = {
        **hook,
        fixture.HOOK_EVENT_NAME_FIELD: fixture.POST_TOOL_USE_HOOK,
        fixture.HOOK_EVENT_ID_FIELD: "posttool-one",
        fixture.TOOL_RESPONSE_FIELD: {fixture.BACKGROUND_TASK_ID_FIELD: "btk9y72c9"},
    }
    support_hooks.deliver_hook(gateway, json.dumps(backgrounded_hook).encode())
