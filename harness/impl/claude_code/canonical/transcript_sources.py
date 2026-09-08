# Copyright (c) 2026 Zhambyl Yermagambet
"""Parse Claude transcript records and resolve child ownership."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from pydantic import ValidationError

from domain import ids as domain_ids
from harness.impl.claude_code import ids as claude_ids
from harness.impl.claude_code.canonical import records, transcript

if TYPE_CHECKING:
    from pathlib import Path

    from harness.models import raw_events as raw_event_models

TEXT_ENCODING = "utf-8"
TRANSCRIPT_SUFFIX = ".jsonl"


@dataclass(frozen=True)
class ActorContext:
    """Contain one transcript actor identity."""

    actor_id: domain_ids.ActorId
    parent_actor_id: domain_ids.ActorId | None


def transcript_record(line: bytes) -> transcript.TranscriptRecord | None:
    """Parse one transcript line.

    Returns:
        The parsed record, if valid.

    """
    try:
        return transcript.parse_line(line.decode(TEXT_ENCODING))
    except (UnicodeDecodeError, ValidationError):
        return None


def team_message_context(
    record: transcript.TeamMessageTranscriptRecord,
    context: raw_event_models.RawEventSourceContext,
    source_path: str,
) -> ActorContext:
    """Return the actor context of one team message.

    Returns:
        The actor context.

    """
    sender_text = record.sender
    keep_context = not sender_text or (
        sender_text == transcript.LEAD_TEAMMATE_ID and context.parent_actor_id is not None
    )
    if keep_context:
        return ActorContext(context.actor_id, context.parent_actor_id)
    sender = (
        context.lead_actor_id
        if sender_text == transcript.LEAD_TEAMMATE_ID
        else claude_ids.actor_id_from_claude_code(
            transcript.teammate_actor_id(source_path, sender_text) or claude_ids.ClaudeCodeActorId(sender_text),
        )
    )
    parent_actor_id = None if sender == context.lead_actor_id else context.lead_actor_id
    return ActorContext(sender, parent_actor_id)


def child_actor_id(child_path: Path) -> domain_ids.ActorId | None:
    """Return the actor ID from one child transcript path.

    Returns:
        The actor ID, if the path has one.

    """
    filename = child_path.name
    actor_name = filename[len("agent-") : -len(TRANSCRIPT_SUFFIX)]
    if not actor_name:
        return None
    return claude_ids.actor_id_from_claude_code(claude_ids.ClaudeCodeActorId(actor_name))


def unique_child_owner(
    owners: list[domain_ids.ActorId],
    call_id: claude_ids.ClaudeCodeCallId,
) -> domain_ids.ActorId | None:
    """Return the only child owner of a tool call.

    Returns:
        The child actor ID, if the call has one owner.

    Raises:
        ValueError: If several child transcripts contain the call.

    """
    if len(owners) > 1:
        message = f"Claude Code tool call {call_id!r} belongs to multiple child transcripts"
        raise ValueError(message)
    return owners[0] if owners else None


def transcript_has_tool_call(path: Path, call_id: claude_ids.ClaudeCodeCallId) -> bool:
    """Return whether a transcript has one native tool call.

    Returns:
        True if the transcript has the call.

    """
    try:
        source = path.open("rb")
    except OSError:
        return False
    with source:
        return any(line_has_tool_call(line, call_id) for line in source)


def line_has_tool_call(line: bytes, call_id: claude_ids.ClaudeCodeCallId) -> bool:
    """Return whether one transcript line has a native tool call.

    Returns:
        True if the line has the call.

    """
    if str(call_id).encode(TEXT_ENCODING) not in line:
        return False
    try:
        assistant = records.AssistantRecord.model_validate_json(line)
    except ValidationError:
        return False
    content = None if assistant.message is None else assistant.message.content
    return isinstance(content, list) and any(
        isinstance(block, records.ToolUseBlock) and block.id == call_id for block in content
    )
