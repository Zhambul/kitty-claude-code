# Copyright (c) 2026 Zhambyl Yermagambet
"""Own tool records models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from harness.impl.codex.ids_conversation_types import CodexTurnId
from harness.impl.codex.ids_session_types import CodexCallId, CodexShellId


@dataclass(frozen=True, kw_only=True)
class SearchRecord:
    """Represent search record."""

    kind: Literal["search"] = "search"
    query: str


@dataclass(frozen=True, kw_only=True)
class ExecRecord:
    """Represent exec record."""

    kind: Literal["exec"] = "exec"
    cmd: str
    call_id: CodexCallId
    turn: CodexTurnId | None = None
    yield_ms: int | None = None
    reports_session_id: bool = False
    ts: str | None = None


@dataclass(frozen=True, kw_only=True)
class ToolRecord:
    """Represent tool record."""

    kind: Literal["tool"] = "tool"
    name: str
    args: str
    call_id: CodexCallId


@dataclass(frozen=True, kw_only=True)
class ExecResultRecord:
    """Represent exec result record."""

    kind: Literal["exec_result"] = "exec_result"
    exit: str | int | None
    output: str
    call_id: CodexCallId
    process_id: CodexShellId | None = None
    running: bool = False
    interrupted: bool = False
    ts: str | None = None


@dataclass(frozen=True, kw_only=True)
class StdinRecord:
    """Represent stdin record."""

    kind: Literal["stdin"] = "stdin"
    text: str
    call_id: CodexCallId
    process_id: CodexShellId


@dataclass(frozen=True, kw_only=True)
class CommandCompletedRecord:
    """Represent command completed record."""

    kind: Literal["command_completed"] = "command_completed"
    process_id: CodexShellId
    command: tuple[str, ...]
    output: str
    exit: int | None
    item_id: str
    turn: CodexTurnId | None = None


@dataclass(frozen=True, kw_only=True)
class McpToolCompletedRecord:
    """Represent mcp tool completed record."""

    kind: Literal["mcp_tool_completed"] = "mcp_tool_completed"
    server: str
    tool: str
    status: str
    item_id: str
    title: str | None = None
    result: str | None = None
    result_is_error: bool = False
    browser_use: bool = False
