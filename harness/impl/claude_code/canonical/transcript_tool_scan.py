# Copyright (c) 2026 Zhambyl Yermagambet
"""Recover Claude tool calls from transcript history."""

from harness.impl.claude_code.canonical import records
from harness.impl.claude_code.canonical.transcript_assignment_scan import _binary_lines, _single_tool_result
from harness.impl.claude_code.canonical.transcript_model_activity import AssistantTranscriptRecord
from harness.impl.claude_code.canonical.transcript_parser import parse_line
from harness.impl.claude_code.ids import ClaudeCodeCallId, ClaudeCodeShellId
from harness.models import raw_events

TEXT_ENCODING = "utf-8"


def tool_call_before(
    path: str,
    before_position: str,
    call_id: ClaudeCodeCallId,
) -> tuple[str, records.ToolArguments] | None:
    """Find the request for a tool result after an application restart.

    Returns:
        Result items.

    """
    try:
        end_position = int(before_position)
    except ValueError:
        return None
    call_bytes = str(call_id).encode(TEXT_ENCODING)
    for line in _binary_lines(path, end_position):
        if call_bytes not in line:
            continue
        match = _tool_call_in_line(line, call_id)
        if match is not None:
            return match
    return None


def _tool_call_in_line(
    line: bytes,
    call_id: ClaudeCodeCallId,
) -> tuple[str, records.ToolArguments] | None:
    try:
        parsed = parse_line(line.decode())
    except UnicodeDecodeError:
        return None
    if not isinstance(parsed, AssistantTranscriptRecord):
        return None
    blocks = None if parsed.message is None else parsed.message.content
    if not isinstance(blocks, list):
        return None
    for block in blocks:
        if isinstance(block, records.ToolUseBlock) and block.id == call_id and block.name:
            return block.name, block.input or records.ToolArguments()
    return None


def background_call(
    path: str,
    task_id: ClaudeCodeShellId,
) -> ClaudeCodeCallId | None:
    """Find the Bash result that introduced one native background task.

    Returns:
        The claude code call id.

    Raises:
        TranslationError: If a raw event cannot be translated.

    """
    if not task_id:
        return None
    candidates: list[ClaudeCodeCallId] = []
    task_bytes = str(task_id).encode(TEXT_ENCODING)
    for line in _binary_lines(path):
        candidate = _background_candidate(line, task_bytes, task_id)
        if candidate is not None and candidate not in candidates:
            candidates.append(candidate)
    if len(candidates) > 1:
        message = f"Claude Code background task {task_id!r} has multiple Bash calls"
        raise raw_events.TranslationError(
            message,
        )
    return candidates[0] if candidates else None


def _background_candidate(
    line: bytes,
    task_bytes: bytes,
    task_id: ClaudeCodeShellId,
) -> ClaudeCodeCallId | None:
    if task_bytes not in line:
        return None
    result = _single_tool_result(line)
    if result is None or result.response.background_task_id != task_id:
        return None
    return result.call_id
