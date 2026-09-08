# Copyright (c) 2026 Zhambyl Yermagambet
"""Define Claude Code finished-tool models."""

from dataclasses import dataclass

from domain.content import Content
from domain.outcomes import Outcome
from harness.impl.claude_code import ids as claude_ids
from harness.impl.claude_code.canonical import records
from harness.impl.claude_code.canonical.tool_kind_values import ToolKind


@dataclass(frozen=True)
class ShellExit:
    """Keep a shell exit code and its canonical outcome."""

    code: int | None
    outcome: Outcome


@dataclass(frozen=True)
class FinishedToolIdentity:
    """Identify a finished tool call and its arguments."""

    call_id: claude_ids.ClaudeCodeCallId
    native_name: str
    arguments: records.ToolArguments
    kind: ToolKind


@dataclass(frozen=True)
class FinishedToolResult:
    """Keep native and parsed tool responses with the canonical result."""

    native_response: records.ToolResponse | records.ToolResponseBlocks | str | None
    response: records.ToolResponse
    answer: Content | None
    outcome: Outcome
    failed: bool


@dataclass(frozen=True)
class TranscriptToolResult:
    """Contain one tool result from a transcript."""

    call_id: claude_ids.ClaudeCodeCallId
    result_text: str
    tool_response: records.ToolResponse | records.ToolResponseBlocks | str | None
    failed: bool
    cancelled: bool = False
