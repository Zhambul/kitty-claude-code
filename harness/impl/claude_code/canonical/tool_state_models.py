# Copyright (c) 2026 Zhambyl Yermagambet
"""Define Claude Code tool-call state models."""

from __future__ import annotations

from dataclasses import dataclass

from domain.ids import SessionId, ShellId
from harness.impl.claude_code import ids as claude_ids
from harness.impl.claude_code.canonical import records


@dataclass(frozen=True)
class RememberedCall:
    """Store one native tool call."""

    session_id: SessionId
    call_id: claude_ids.ClaudeCodeCallId
    native_name: str
    arguments: records.ToolArguments


@dataclass
class MonitorState:
    """Store one monitor state."""

    session_id: SessionId
    task_id: claude_ids.ClaudeCodeShellId
    shell_id: ShellId
    event_count: int = 0


@dataclass(frozen=True)
class BackgroundTaskState:
    """Store one background task state."""

    session_id: SessionId
    task_id: claude_ids.ClaudeCodeShellId
    shell_id: ShellId


@dataclass(frozen=True)
class AgentAssignmentState:
    """Store one agent assignment state."""

    session_id: SessionId
    actor_id: claude_ids.ClaudeCodeActorId
    call_id: claude_ids.ClaudeCodeCallId


def remembered_arguments(remembered_call: RememberedCall | None) -> records.ToolArguments:
    """Read arguments from a remembered tool call.

    Returns:
        The saved arguments, or empty arguments if the call is not known.

    """
    if remembered_call is None:
        return records.ToolArguments()
    return remembered_call.arguments
