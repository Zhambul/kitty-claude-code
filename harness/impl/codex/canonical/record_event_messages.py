# Copyright (c) 2026 Zhambyl Yermagambet
"""Own event messages models."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from harness.impl.codex.canonical.record_config import FOREIGN, OPEN_FOREIGN, ForeignMetadata
from harness.impl.codex.canonical.record_item_registry import ItemTypeHeader
from harness.impl.codex.ids_conversation_types import CodexTurnId
from harness.impl.codex.ids_session_types import CodexCallId


class ItemCompletedHeaderPayload(BaseModel):
    """Represent item completed header payload."""

    model_config = OPEN_FOREIGN
    type: Literal["item_completed"] = "item_completed"
    completed_item_header: ItemTypeHeader | None = Field(default=None, alias="item")


class TurnAbortedPayload(BaseModel):
    """Represent turn aborted payload."""

    model_config = FOREIGN
    type: Literal["turn_aborted"] = "turn_aborted"
    turn_id: CodexTurnId | None = None
    reason: str | None = None
    completed_at: str | int | float | None = None
    duration_ms: int | None = None
    started_at: str | int | float | None = None


class UserMessagePayload(BaseModel):
    """Represent user message payload."""

    model_config = FOREIGN
    type: Literal["user_message"] = "user_message"
    message: str | None = None
    client_id: str | None = None
    # Attachment lists — every measured rollout carries them EMPTY, so their
    # populated element shape is not yet known (module header: declare what
    # reality allows, not what it might one day be).
    images: list[ForeignMetadata] | None = None
    local_images: list[ForeignMetadata] | None = None
    text_elements: list[ForeignMetadata] | None = None
    audio: list[ForeignMetadata] | None = None
    local_audio: list[ForeignMetadata] | None = None


class AgentReasoningPayload(BaseModel):
    """Represent agent reasoning payload."""

    model_config = FOREIGN
    type: Literal["agent_reasoning"] = "agent_reasoning"
    text: str | None = None


class AgentMessagePayload(BaseModel):
    """Represent agent message payload."""

    model_config = FOREIGN
    type: Literal["agent_message"] = "agent_message"
    message: str | None = None
    phase: str | None = None
    # Always None in every measured rollout; its populated shape is unknown.
    memory_citation: None = None


class WebSearchAction(BaseModel):
    """Represent web search action."""

    model_config = FOREIGN
    type: str | None = None
    query: str | None = None
    queries: list[str] | None = None
    url: str | None = None
    pattern: str | None = None


class WebSearchEndPayload(BaseModel):
    """Represent web search end payload."""

    model_config = FOREIGN
    type: Literal["web_search_end"] = "web_search_end"
    query: str | None = None
    action: WebSearchAction | None = None
    call_id: CodexCallId | None = None
    search_results: list[ForeignMetadata] | None = Field(default=None, alias="results")
