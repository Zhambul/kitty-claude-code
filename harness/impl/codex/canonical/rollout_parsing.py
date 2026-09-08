# Copyright (c) 2026 Zhambyl Yermagambet
"""Parse the event and response registers in a Codex rollout."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import ValidationError

from harness.impl.codex.canonical import (
    record_event_documents,
    record_event_messages,
    record_item_registry,
    record_response_documents,
    record_rollout_headers,
    record_terminal_records,
)
from harness.impl.codex.canonical.events import EVENTS, CodexEventType, parse_event
from harness.impl.codex.canonical.items import RESPONSES, CodexResponseType, parse_response
from harness.impl.codex.canonical.rollout_stamps import stamp
from harness.impl.codex.canonical.rollout_toplevel import parse_top_level_line

if TYPE_CHECKING:
    from collections.abc import Mapping

KINDS = frozenset((
    "turn_context",
    "usage",
    "patch",
    "compact",
    "task_started",
    "task_complete",
    "turn_aborted",
    "prompt",
    "skill",
    "reasoning",
    "message",
    "search",
    "exec",
    "exec_result",
    "stdin",
    "command_completed",
    "mcp_tool_completed",
    "chat",
    "think",
    "patch_call",
    "ask",
    "plan",
    "settings",
    "compact_boundary",
    "tool",
    "actor_activity",
    "collaboration_call",
    "task_list",
    "goal",
    "goal_tool",
    "tool_batch",
    "unmapped_tool",
    "bad",
    "world_state",
    "covered_item",
    "empty",
))


def parse(document: Mapping[str, object]) -> record_terminal_records.RolloutRecord | None:
    """Parse an already-decoded rollout document.

    Returns:
        The typed record, or None for an unsupported record type.

    """
    return parse_line(record_rollout_headers.RolloutInput(root=document).model_dump_json())


def parse_line(line: str) -> record_terminal_records.RolloutRecord | None:
    """Parse one Codex rollout JSONL line.

    Returns:
        The typed record, a bad record for an invalid header, or None for an unsupported type.

    """
    try:
        header = record_rollout_headers.RolloutHeader.model_validate_json(line)
    except ValidationError:
        return verified_record(record_terminal_records.BadRecord(raw=line))
    if header.type == "event_msg":
        parsed_record = parse_event_line(line)
    elif header.type == "response_item":
        parsed_record = parse_response_line(line)
    else:
        parsed_record = parse_top_level_line(line, header)
    return verified_record(parsed_record)


def verified_record(
    parsed_record: record_terminal_records.RolloutRecord | None,
) -> record_terminal_records.RolloutRecord | None:
    """Reject record kinds that the rollout vocabulary does not declare.

    Returns:
        The supplied record or None, without changes.

    Raises:
        RuntimeError: If the parser produced an undeclared record kind.

    """
    if parsed_record is None or parsed_record.kind in KINDS:
        return parsed_record
    msg = f"undeclared Codex rollout record kind: {parsed_record.kind!r}"
    raise RuntimeError(msg)


def parse_event_line(line: str) -> record_terminal_records.RolloutRecord | None:
    """Parse one event-register line.

    Returns:
        The translated event with its timestamp, or None for an unsupported event or item type.

    """
    payload_type = record_rollout_headers.PayloadHeaderDocument.model_validate_json(line).payload.type
    try:
        event_type = CodexEventType(payload_type or "")
    except ValueError:
        return None
    if event_type not in EVENTS or (event_type is CodexEventType.ITEM_COMPLETED and not known_completed_item(line)):
        return None
    event_document = record_event_documents.EventDocument.model_validate_json(line)
    return stamp(parse_event(event_document.payload), event_document.timestamp)


def known_completed_item(line: str) -> bool:
    """Return whether an item-completed record has a supported item type.

    Returns:
        Whether an item-completed record has a supported item type.

    """
    item_header = (
        record_rollout_headers
        .RolloutDocument[record_event_messages.ItemCompletedHeaderPayload]
        .model_validate_json(line)
        .payload
    )
    completed_header = item_header.completed_item_header
    completed_type = "" if completed_header is None else completed_header.type
    try:
        record_item_registry.ItemCompletedType(completed_type or "")
    except ValueError:
        return False
    return True


def parse_response_line(line: str) -> record_terminal_records.RolloutRecord | None:
    """Parse one response-register line.

    Returns:
        The translated response with its timestamp, or None for an unsupported response type.

    """
    payload_type = record_rollout_headers.PayloadHeaderDocument.model_validate_json(line).payload.type
    try:
        response_type = CodexResponseType(payload_type or "")
    except ValueError:
        return None
    if response_type not in RESPONSES:
        return None
    response_document = record_response_documents.ResponseDocument.model_validate_json(line)
    return stamp(parse_response(response_document.payload), response_document.timestamp)
