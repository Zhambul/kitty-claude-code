# Copyright (c) 2026 Zhambyl Yermagambet
"""Recover Claude prompt ancestry from transcript history."""

from pydantic import ValidationError

from harness.impl.claude_code.canonical import records
from harness.impl.claude_code.canonical.transcript_assignment_scan import _binary_lines
from harness.impl.claude_code.canonical.transcript_model_core import PromptTranscriptRecord
from harness.impl.claude_code.canonical.transcript_model_notifications import AncestryLine
from harness.impl.claude_code.canonical.transcript_parser import parse_line
from harness.impl.claude_code.ids import ClaudeCodeTurnId


def is_task_prompt(document: records.TranscriptDocument) -> bool:
    """Check for a delivered task notification.

    Returns:
        True if the record is a task prompt, not a queue update.

    """
    return (
        document.type == "user"
        and document.origin is not None
        and document.origin.kind == "task-notification"
    )


def prompt_turn_before(
    path: str,
    before_position: str,
    parent_uuid: str | None,
) -> ClaudeCodeTurnId | None:
    """Find the prompt ancestor of a response after an application restart.

    Returns:
        The claude code turn id.

    """
    if parent_uuid is None:
        return None
    try:
        end_position = int(before_position)
    except ValueError:
        return None
    parents, prompts = _turn_ancestry(path, end_position)
    return _prompt_ancestor(parent_uuid, parents, prompts)


def _turn_ancestry(
    path: str,
    end_position: int,
) -> tuple[dict[str, str | None], set[str]]:
    parents: dict[str, str | None] = {}
    prompts: set[str] = set()
    for line in _binary_lines(path, end_position):
        ancestry = _ancestry_line(line)
        if ancestry is None:
            continue
        parents[ancestry.identity] = ancestry.parent_identity
        if ancestry.is_prompt:
            prompts.add(ancestry.identity)
    return parents, prompts


def _ancestry_line(line: bytes) -> AncestryLine | None:
    try:
        document = records.TranscriptDocument.model_validate_json(line)
    except ValidationError:
        return None
    if document.uuid is None:
        return None
    try:
        parsed = parse_line(line.decode())
    except (UnicodeDecodeError, ValidationError):
        parsed = None
    is_prompt = is_task_prompt(document) or (isinstance(parsed, PromptTranscriptRecord) and not parsed.meta)
    return AncestryLine(document.uuid, document.parent_uuid, is_prompt)


def _prompt_ancestor(
    parent_uuid: str,
    parents: dict[str, str | None],
    prompts: set[str],
) -> ClaudeCodeTurnId | None:
    identity = parent_uuid
    visited: set[str] = set()
    while identity not in visited:
        if identity in prompts:
            return ClaudeCodeTurnId(identity)
        visited.add(identity)
        parent = parents.get(identity)
        if parent is None:
            return None
        identity = parent
    return None
