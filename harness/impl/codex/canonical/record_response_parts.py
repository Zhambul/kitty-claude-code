# Copyright (c) 2026 Zhambyl Yermagambet
"""Own response parts models."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, Field

from harness.impl.codex.canonical.record_config import FOREIGN, OPEN_FOREIGN
from harness.impl.codex.ids_conversation_types import CodexTurnId
from harness.impl.codex.ids_session_types import CodexCallId


class ChatMessageMetadata(BaseModel):
    """Represent chat message metadata."""

    model_config = FOREIGN
    turn_id: CodexTurnId | None = None
    create_time: float | None = None
    content_item_kinds: list[str] | None = None


class WebSearchCallAction(BaseModel):
    """Represent web search call action."""

    model_config = FOREIGN
    type: str | None = None
    query: str | None = None
    queries: list[str] | None = None
    url: str | None = None
    pattern: str | None = None


class WebSearchCallPayload(BaseModel):
    """Represent web search call payload."""

    model_config = FOREIGN
    type: Literal["web_search_call"] = "web_search_call"
    id: str | None = None
    action: WebSearchCallAction | None = None
    status: str | None = None
    internal_chat_message_metadata_passthrough: ChatMessageMetadata | None = None


class ContentPart(BaseModel):
    """Represent content part."""

    model_config = FOREIGN
    type: str | None = None
    text: str | None = None
    image_url: str | None = None
    detail: str | None = None


class AgentCommunicationPayload(BaseModel):
    """A v2 agent-to-agent message whose task body can be encrypted."""

    model_config = OPEN_FOREIGN
    type: Literal["agent_message"] = "agent_message"


class NodeReplResultDocument(BaseModel):
    """The outer result document returned by the node-repl MCP tool."""

    model_config = FOREIGN
    content: list[ContentPart]
    is_error: Annotated[bool, Field(alias="isError")] = False


class FunctionCallOutputPayload(BaseModel):
    """Represent function call output payload."""

    model_config = FOREIGN
    type: Literal["function_call_output"] = "function_call_output"
    id: str | None = None
    output: str | list[ContentPart | str] | None = None
    call_id: CodexCallId | None = None
    internal_chat_message_metadata_passthrough: ChatMessageMetadata | None = None
