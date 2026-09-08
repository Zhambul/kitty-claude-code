# Copyright (c) 2026 Zhambyl Yermagambet
"""Parse Codex rollout records outside its two payload registers."""

from __future__ import annotations

from enum import StrEnum
from types import MappingProxyType
from typing import TYPE_CHECKING

from harness.impl.codex.canonical import (
    record_context_records,
    record_interaction_records,
    record_result_documents,
    record_rollout_headers,
    record_terminal_records,
    record_turn_payloads,
    record_usage_documents,
)

if TYPE_CHECKING:
    from collections.abc import Mapping

    from pydantic import BaseModel


class CodexTopLevelType(StrEnum):
    """Name supported top-level rollout records."""

    TURN_CONTEXT = "turn_context"
    USAGE = "token_usage_record"
    COMPACTED = "compacted"
    WORLD_STATE = "world_state"
    INTER_AGENT_COMMUNICATION_METADATA = "inter_agent_communication_metadata"


TOP_LEVEL_DOCUMENTS: Mapping[CodexTopLevelType, type[BaseModel]] = MappingProxyType({
    CodexTopLevelType.TURN_CONTEXT: record_result_documents.TurnContextDocument,
    CodexTopLevelType.USAGE: record_usage_documents.TokenUsageDocument,
    CodexTopLevelType.COMPACTED: record_result_documents.CompactedDocument,
    CodexTopLevelType.WORLD_STATE: record_result_documents.WorldStateDocument,
    CodexTopLevelType.INTER_AGENT_COMMUNICATION_METADATA: (
        record_result_documents.InterAgentCommunicationMetadataDocument
    ),
})


def parse_top_level_line(
    line: str,
    header: record_rollout_headers.RolloutHeader,
) -> record_terminal_records.RolloutRecord | None:
    """Parse one record outside the event and response registers.

    Returns:
        The translated top-level record, or None for an unsupported type.

    """
    try:
        top_type = CodexTopLevelType(header.type or "")
    except ValueError:
        return None
    if top_type not in TOP_LEVEL_DOCUMENTS:
        return None
    if top_type is CodexTopLevelType.TURN_CONTEXT:
        return turn_context(record_result_documents.TurnContextDocument.model_validate_json(line).payload)
    if top_type is CodexTopLevelType.COMPACTED:
        return compacted(record_result_documents.CompactedDocument.model_validate_json(line).payload)
    return remaining_top_level_line(line, top_type)


def turn_context(payload: record_turn_payloads.TurnContextPayload) -> record_context_records.TurnContextRecord:
    """Translate a turn context payload.

    Returns:
        The selected model and effort, using collaboration settings when present.

    """
    settings = payload.collaboration_mode.settings if payload.collaboration_mode else None
    effort = settings.reasoning_effort if settings else payload.effort
    return record_context_records.TurnContextRecord(model=payload.model, effort=effort)


def compacted(payload: record_turn_payloads.CompactedPayload) -> record_interaction_records.CompactBoundaryRecord:
    """Translate a context compaction payload.

    Returns:
        The compaction boundary with its summary, replacement count, and window identifiers.

    """
    replacement_history = payload.replacement_history
    return record_interaction_records.CompactBoundaryRecord(
        message=payload.message or "",
        context=(payload.message or "").strip(),
        replaced=0 if replacement_history is None else len(replacement_history),
        window_id=payload.window_id,
        previous_window_id=payload.previous_window_id,
    )


def remaining_top_level_line(
    line: str, codex_top_level_type: CodexTopLevelType,
) -> record_terminal_records.RolloutRecord:
    """Parse the supported top-level records not handled by direct branches.

    Returns:
        A world-state record, or an empty record for usage and communication metadata.

    """
    if codex_top_level_type is CodexTopLevelType.USAGE:
        record_usage_documents.TokenUsageDocument.model_validate_json(line)
        # Token count events supply the same usage. Do not count it twice.
        return record_terminal_records.EmptyRecord()
    if codex_top_level_type is CodexTopLevelType.INTER_AGENT_COMMUNICATION_METADATA:
        record_result_documents.InterAgentCommunicationMetadataDocument.model_validate_json(line)
        return record_terminal_records.EmptyRecord()
    record_result_documents.WorldStateDocument.model_validate_json(line)
    return record_terminal_records.WorldStateRecord()
