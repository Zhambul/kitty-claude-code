# Copyright (c) 2026 Zhambyl Yermagambet
"""Recover Claude assignment calls from transcript history."""

from collections.abc import Iterator
from pathlib import Path

from pydantic import ValidationError

from harness.impl.claude_code.canonical import records
from harness.impl.claude_code.canonical.transcript_model_notifications import SingleToolResult
from harness.impl.claude_code.canonical.transcript_teammates import teammate_meta
from harness.impl.claude_code.ids import ClaudeCodeActorId, ClaudeCodeCallId
from harness.models import raw_events

TEXT_ENCODING = "utf-8"


def _binary_lines(
    path: str,
    before_position: int | None = None,
) -> Iterator[bytes]:
    try:
        with Path(path).open("rb") as source:
            while before_position is None or source.tell() < before_position:
                line = source.readline()
                if not line:
                    return
                yield line
    except OSError:
        return


def assignment_call_before(
    path: str,
    before_position: str,
    actor_id: ClaudeCodeActorId,
) -> ClaudeCodeCallId | None:
    """Find the Agent result that introduced one async child before a position.

    Returns:
        The claude code call id.

    Raises:
        TranslationError: If a raw event cannot be translated.

    """
    try:
        end_position = int(before_position)
    except ValueError:
        return None
    teammate_name = str(teammate_meta(path, actor_id).name or "")
    candidates = _assignment_candidates(
        path,
        end_position,
        actor_id,
        teammate_name,
    )
    if len(candidates) > 1:
        message = f"Claude Code actor {actor_id!r} has multiple Agent assignments"
        raise raw_events.TranslationError(
            message,
        )
    return candidates[0] if candidates else None


def _assignment_candidates(
    path: str,
    end_position: int,
    actor_id: ClaudeCodeActorId,
    teammate_name: str,
) -> list[ClaudeCodeCallId]:
    candidates: list[ClaudeCodeCallId] = []
    for line in _binary_lines(path, end_position):
        candidate = _assignment_candidate(line, actor_id, teammate_name)
        if candidate is not None and candidate not in candidates:
            candidates.append(candidate)
    return candidates


def _assignment_candidate(
    line: bytes,
    actor_id: ClaudeCodeActorId,
    teammate_name: str,
) -> ClaudeCodeCallId | None:
    actor_not_named = str(actor_id).encode(TEXT_ENCODING) not in line
    teammate_not_named = not teammate_name or teammate_name.encode(TEXT_ENCODING) not in line
    if actor_not_named and teammate_not_named:
        return None
    result = _single_tool_result(line)
    if result is None or not _response_matches_actor(result.response, actor_id, teammate_name):
        return None
    return result.call_id


def _response_matches_actor(
    response: records.ToolResponse,
    actor_id: ClaudeCodeActorId,
    teammate_name: str,
) -> bool:
    response_actor_ids = {
        str(response.external_agent_id or ""),
        str(response.teammate_id or ""),
    }
    actor_matches = str(actor_id) in response_actor_ids
    name_matches = bool(teammate_name) and response.name == teammate_name
    return actor_matches or name_matches


def _single_tool_result(
    line: bytes,
) -> SingleToolResult | None:
    try:
        user_record = records.UserRecord.model_validate_json(line)
    except ValidationError:
        return None
    response = user_record.tool_use_result
    if not isinstance(response, records.ToolResponse):
        return None
    content_blocks = None if user_record.message is None else user_record.message.content
    if not isinstance(content_blocks, list):
        return None
    result_blocks = [block for block in content_blocks if isinstance(block, records.ToolResultBlock)]
    if len(result_blocks) != 1 or not result_blocks[0].tool_use_id:
        return None
    return SingleToolResult(
        response,
        ClaudeCodeCallId(result_blocks[0].tool_use_id),
    )
