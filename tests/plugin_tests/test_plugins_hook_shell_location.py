# Copyright (c) 2026 Zhambyl Yermagambet
"""Shell output location tests."""

import json
from pathlib import Path

import pytest

from domain.event_shell import (
    ShellOutputLocated,
)
from harness.impl.claude_code import shell as claude_shell
from harness.impl.claude_code.canonical.records import HookPayload
from harness.impl.claude_code.hooks import foreground as claude_foreground, gateway as claude_hooks
from tests.plugin_tests import support_hooks, vocabulary as fixture
from tests.plugin_tests.hook_common_support import encoded_json_document


def test_claude_fg_prepare_rewrites_command_into(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Verify claude foreground prepare rewrites the command into an output location."""
    monkeypatch.setenv(fixture.CLAUDE_CONFIG_DIR_ENV, str(tmp_path / fixture.CLAUDE))
    document = {
        fixture.SESSION_ID_FIELD: fixture.SESSION_ONE_ID,
        fixture.AGENT_ID_FIELD: fixture.CHILD_ONE_ID,
        fixture.CWD_FIELD: str(tmp_path),
        fixture.TOOL_USE_ID_FIELD: fixture.COMMAND_ONE,
        fixture.TOOL_INPUT_FIELD: {fixture.COMMAND_FIELD: "printf hello"},
    }

    prepared = claude_foreground.prepare(HookPayload.model_validate(document))

    assert prepared is not None
    native_output = json.loads(prepared.reply)
    updated_command = native_output[fixture.HOOK_SPECIFIC_OUTPUT]["updatedInput"][fixture.COMMAND_FIELD]
    assert native_output[fixture.HOOK_SPECIFIC_OUTPUT]["permissionDecision"] == fixture.ALLOW
    assert "tee -a" in updated_command
    assert len(prepared.locations) == 1
    located = prepared.locations[0]
    _assert_foreground_location_identity(located)
    _assert_foreground_location_storage(located, updated_command)


def _assert_foreground_location_identity(located: ShellOutputLocated) -> None:
    """Verify the foreground output location identity."""
    assert located.shell_id == fixture.COMMAND_ONE
    assert located.until == "shell_finished"
    assert located.chunk_source_type == fixture.FOREGROUND_OUTPUT_ID


def _assert_foreground_location_storage(
    located: ShellOutputLocated,
    updated_command: str,
) -> None:
    """Verify the foreground output location storage policy."""
    assert located.delete_source is True
    assert located.source_path in updated_command


def test_claude_shell_finds_every_static_redirect(tmp_path: Path) -> None:
    """Verify claude shell finds every static redirect and pipe sink."""
    command = (
        "cd nested && task > first.log 2> /test-data/errors.log; "
        "echo exit >> first.log; printf pipe | tee -a /test-data/pipe-one.log /test-data/pipe-two.log >/dev/null"
    )

    found = claude_shell.redirected_outputs(command, str(tmp_path))

    assert [(redirect.path, redirect.append) for redirect in found] == [
        (str(tmp_path / "nested" / "first.log"), False),
        ("/test-data/errors.log", False),
        ("/test-data/pipe-one.log", True),
        ("/test-data/pipe-two.log", True),
    ]


def test_claude_shell_finds_pipe_sink_in_process() -> None:
    """Verify claude shell finds a pipe sink in process substitution."""
    found = claude_shell.redirected_outputs(
        "task > >(tee /test-data/process-output.log)",
        fixture.WORK_PATH,
    )

    assert [(redirect.path, redirect.append) for redirect in found] == [
        ("/test-data/process-output.log", False),
    ]


def test_claude_bg_pretool_locates_all_redirected() -> None:
    """Verify claude background pretool locates all redirected files."""
    document = {
        fixture.SESSION_ID_FIELD: fixture.CLAUDE_SESSION_ID,
        fixture.TRANSCRIPT_PATH: fixture.WORK_CLAUDE_JSONL_PATH,
        fixture.CWD_FIELD: fixture.WORK_PATH,
        fixture.HOOK_EVENT_NAME_FIELD: fixture.PRE_TOOL_USE_HOOK,
        fixture.HOOK_EVENT_ID_FIELD: "pre-background-one",
        fixture.TOOL_NAME_FIELD: fixture.BASH_TOOL,
        fixture.TOOL_USE_ID_FIELD: fixture.BACKGROUND_ONE,
        fixture.TOOL_INPUT_FIELD: {
            fixture.COMMAND_FIELD: (
                "deploy > /test-data/deploy.log 2>&1; echo done >> /test-data/deploy.log; "
                "printf pipe | tee /test-data/pipe.log >/dev/null"
            ),
            fixture.RUN_IN_BACKGROUND_FIELD: True,
        },
    }

    response = claude_hooks.ClaudeHookGateway().receive_hook(
        support_hooks.hook_request(encoded_json_document(document)),
    )

    directives = [row for row in response.raw_events if row.source_type == fixture.OUTPUT_LOCATION_ID]
    directive_documents = [json.loads(row.payload) for row in directives]
    assert response.reply == b""
    assert [document[fixture.SOURCE_PATH_FIELD] for document in directive_documents] == [
        "/test-data/deploy.log",
        "/test-data/pipe.log",
    ]
    assert all(document[fixture.UNTIL] == fixture.SESSION_FINISHED_ID for document in directive_documents)
    assert len({row.raw_event_id for row in directives}) == len(directives)


def test_claude_monitor_pretool_locates() -> None:
    """Verify claude monitor pretool locates redirected files without rewriting input."""
    document = {
        fixture.SESSION_ID_FIELD: fixture.CLAUDE_SESSION_ID,
        fixture.TRANSCRIPT_PATH: fixture.WORK_CLAUDE_JSONL_PATH,
        fixture.CWD_FIELD: fixture.WORK_PATH,
        fixture.HOOK_EVENT_NAME_FIELD: fixture.PRE_TOOL_USE_HOOK,
        fixture.HOOK_EVENT_ID_FIELD: "pre-monitor-one",
        fixture.TOOL_NAME_FIELD: fixture.MONITOR_TOOL,
        fixture.TOOL_USE_ID_FIELD: "monitor-one",
        fixture.TOOL_INPUT_FIELD: {
            fixture.COMMAND_FIELD: "watch-command > /test-data/monitor.log 2>&1",
            fixture.DESCRIPTION_FIELD: "watch changes",
            "persistent": True,
        },
    }

    response = claude_hooks.ClaudeHookGateway().receive_hook(
        support_hooks.hook_request(encoded_json_document(document)),
    )

    directives = [row for row in response.raw_events if row.source_type == fixture.OUTPUT_LOCATION_ID]
    assert response.reply == b""
    assert len(directives) == 1
    assert json.loads(directives[0].payload)[fixture.SOURCE_PATH_FIELD] == "/test-data/monitor.log"
    assert json.loads(directives[0].payload)[fixture.UNTIL] == fixture.SESSION_FINISHED_ID
