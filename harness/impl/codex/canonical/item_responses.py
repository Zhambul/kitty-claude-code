# Copyright (c) 2026 Zhambyl Yermagambet
"""Item responses."""

from __future__ import annotations

from enum import StrEnum
from types import MappingProxyType
from typing import TYPE_CHECKING

from harness.impl.codex.canonical import record_response_documents, record_response_parts, record_terminal_records
from harness.impl.codex.canonical.item_function_calls import _rsp_custom_tool_call, _rsp_function_call
from harness.impl.codex.canonical.item_javascript_records import _rsp_reasoning
from harness.impl.codex.canonical.item_output_records import _rsp_custom_tool_call_output
from harness.impl.codex.canonical.item_response_content import (
    _rsp_function_call_output,
    _rsp_message,
    _rsp_web_search_call,
)
from harness.impl.codex.canonical.vocabulary import (
    empty_record,
)

if TYPE_CHECKING:
    from collections.abc import Mapping

    from pydantic import BaseModel


class CodexResponseType(StrEnum):
    """Represent codex response type."""

    AGENT_MESSAGE = "agent_message"
    WEB_SEARCH_CALL = "web_search_call"
    FUNCTION_CALL_OUTPUT = "function_call_output"
    FUNCTION_CALL = "function_call"
    MESSAGE = "message"
    REASONING = "reasoning"
    CUSTOM_TOOL_CALL = "custom_tool_call"
    CUSTOM_TOOL_CALL_OUTPUT = "custom_tool_call_output"


def _remaining_response(payload: BaseModel) -> record_terminal_records.RolloutRecord | None:
    if isinstance(payload, record_response_documents.MessagePayload):
        return _rsp_message(payload)
    if isinstance(payload, record_response_documents.ReasoningPayload):
        return _rsp_reasoning(payload)
    if isinstance(payload, record_response_documents.CustomToolCallPayload):
        return _rsp_custom_tool_call(payload)
    if isinstance(payload, record_response_documents.CustomToolCallOutputPayload):
        return _rsp_custom_tool_call_output(payload)
    return None


RESPONSES: Mapping[CodexResponseType, type[BaseModel]] = MappingProxyType({
    CodexResponseType.AGENT_MESSAGE: record_response_parts.AgentCommunicationPayload,
    CodexResponseType.WEB_SEARCH_CALL: record_response_parts.WebSearchCallPayload,
    CodexResponseType.FUNCTION_CALL_OUTPUT: record_response_parts.FunctionCallOutputPayload,
    CodexResponseType.FUNCTION_CALL: record_response_documents.FunctionCallPayload,
    CodexResponseType.MESSAGE: record_response_documents.MessagePayload,
    CodexResponseType.REASONING: record_response_documents.ReasoningPayload,
    CodexResponseType.CUSTOM_TOOL_CALL: record_response_documents.CustomToolCallPayload,
    CodexResponseType.CUSTOM_TOOL_CALL_OUTPUT: record_response_documents.CustomToolCallOutputPayload,
})


def parse_response(payload: BaseModel) -> record_terminal_records.RolloutRecord | None:
    """Parse response.

    Returns:
        The rollout record.

    """
    if isinstance(payload, record_response_parts.AgentCommunicationPayload):
        return empty_record()
    if isinstance(payload, record_response_parts.WebSearchCallPayload):
        return _rsp_web_search_call(payload)
    if isinstance(payload, record_response_parts.FunctionCallOutputPayload):
        return _rsp_function_call_output(payload)
    if isinstance(payload, record_response_documents.FunctionCallPayload):
        return _rsp_function_call(payload)
    return _remaining_response(payload)
