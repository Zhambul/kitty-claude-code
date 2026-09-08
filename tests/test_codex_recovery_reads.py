# Copyright (c) 2026 Zhambyl Yermagambet
"""Check that shell recovery parses only candidate records."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest

from harness.impl.codex.canonical.translator_recovery import (
    backward_lines,
    process_shell_call_from_line,
)
from harness.impl.codex.ids_session_types import CodexCallId, CodexShellId

if TYPE_CHECKING:
    from pathlib import Path

LONG_RECORD_REPETITIONS = 50
TYPE_FIELD = "type"


@pytest.mark.parametrize("chunk_size", [1, 7, 64])
def test_backward_reads_keep_complete_lines(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, chunk_size: int) -> None:
    """Keep long records and stop at the requested source position."""
    monkeypatch.setattr("harness.impl.codex.canonical.translator_recovery.BACKWARD_SCAN_CHUNK_BYTES", chunk_size)
    lines = [
        b'{"first":true}',
        json.dumps({"text": "long record " * LONG_RECORD_REPETITIONS}).encode(),
        b'{"last":true}',
    ]
    prefix = b"\n".join([*lines, b""])
    path = tmp_path / "rollout.jsonl"
    path.write_bytes(b"".join((prefix, b'{"later":true}\n')))
    assert (
        list(backward_lines(str(path), len(prefix)))
        == list(reversed(lines))
    )


def test_recovery_skips_unrelated_arguments() -> None:
    """Skip old JavaScript calls with no matching process result."""
    line = json.dumps({
        TYPE_FIELD: "response_item",
        "payload": {
            TYPE_FIELD: "custom_tool_call",
            "name": "exec",
            "call_id": "unrelated",
            "input": 'tools.exec_command({"cmd":"echo old"})',
        },
    }).encode()
    with patch("harness.impl.codex.canonical.rollout.parse_line") as parse:
        assert process_shell_call_from_line(line, CodexShellId("88"), {}) is None
        parse.assert_not_called()


def test_recovery_parses_selected_call() -> None:
    """Keep the original call when its result names the requested process."""
    result = json.dumps({
        TYPE_FIELD: "response_item",
        "payload": {
            TYPE_FIELD: "custom_tool_call_output",
            "call_id": "command",
            "output": json.dumps({"session_id": 88, "output": ""}),
        },
    }).encode()
    call = json.dumps({
        TYPE_FIELD: "response_item",
        "payload": {
            TYPE_FIELD: "custom_tool_call",
            "name": "exec",
            "call_id": "command",
            "input": 'tools.exec_command({"cmd":"sleep 30"})',
        },
    }).encode()
    matches: dict[CodexCallId, bool] = {}
    assert process_shell_call_from_line(result, CodexShellId("88"), matches) is None
    recovered = process_shell_call_from_line(call, CodexShellId("88"), matches)
    assert recovered is not None
    assert recovered.cmd == "sleep 30"
