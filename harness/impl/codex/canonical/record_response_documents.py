# Copyright (c) 2026 Zhambyl Yermagambet
"""Own response documents models."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, Field

from harness.impl.codex.canonical.record_config import FOREIGN
from harness.impl.codex.canonical.record_response_parts import (
    AgentCommunicationPayload,
    ChatMessageMetadata,
    ContentPart,
    FunctionCallOutputPayload,
    WebSearchCallPayload,
)
from harness.impl.codex.canonical.record_rollout_headers import RolloutDocument
from harness.impl.codex.ids_session_types import CodexCallId


class MessagePayload(BaseModel):
    """Represent message payload."""

    model_config = FOREIGN
    type: Literal["message"] = "message"
    id: str | None = None
    content: str | list[ContentPart | str] | None = None
    role: str | None = None
    phase: str | None = None
    internal_chat_message_metadata_passthrough: ChatMessageMetadata | None = None


class ReasoningPayload(BaseModel):
    """Represent reasoning payload."""

    model_config = FOREIGN
    type: Literal["reasoning"] = "reasoning"
    id: str | None = None
    summary: str | list[ContentPart | str] | None = None
    # Always None where `summary` carries the text (encrypted_content holds
    # it instead when the think is stored encrypted) — never both populated
    # in any measured rollout, so `content`'s populated shape is unknown.
    content: None = None
    encrypted_content: str | None = None
    internal_chat_message_metadata_passthrough: ChatMessageMetadata | None = None


class CustomToolCallPayload(BaseModel):
    """Represent custom tool call payload."""

    model_config = FOREIGN
    type: Literal["custom_tool_call"] = "custom_tool_call"
    id: str | None = None
    name: str | None = None
    input: str | list[ContentPart | str] | None = None
    call_id: CodexCallId | None = None
    status: str | None = None
    internal_chat_message_metadata_passthrough: ChatMessageMetadata | None = None


class CustomToolCallOutputPayload(BaseModel):
    """Represent custom tool call output payload."""

    model_config = FOREIGN
    type: Literal["custom_tool_call_output"] = "custom_tool_call_output"
    id: str | None = None
    output: str | list[ContentPart | str] | None = None
    call_id: CodexCallId | None = None
    internal_chat_message_metadata_passthrough: ChatMessageMetadata | None = None


class FunctionCallPayload(BaseModel):
    """Represent function call payload."""

    model_config = FOREIGN
    type: Literal["function_call"] = "function_call"
    id: str | None = None
    name: str | None = None
    namespace: str | None = None
    internal_chat_message_metadata_passthrough: ChatMessageMetadata | None = None
    call_id: CodexCallId | None = None
    arguments: str | None = None


ResponsePayload = Annotated[
    WebSearchCallPayload
    | FunctionCallOutputPayload
    | MessagePayload
    | ReasoningPayload
    | CustomToolCallPayload
    | CustomToolCallOutputPayload
    | FunctionCallPayload
    | AgentCommunicationPayload,
    Field(discriminator="type"),
]


class ResponseDocument(RolloutDocument[ResponsePayload]):
    """Represent response document."""

    type: Literal["response_item"] = "response_item"
