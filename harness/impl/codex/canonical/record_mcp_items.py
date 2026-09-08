# Copyright (c) 2026 Zhambyl Yermagambet
"""Own mcp items models."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from harness.impl.codex.canonical.record_config import OPEN_FOREIGN


class McpToolCallArguments(BaseModel):
    """Represent mcp tool call arguments."""

    model_config = OPEN_FOREIGN
    title: str | None = None


class McpToolResultContent(BaseModel):
    """Represent mcp tool result content."""

    model_config = OPEN_FOREIGN
    type: str | None = None
    text: str | None = None


class McpToolResultMetadata(BaseModel):
    """Represent mcp tool result metadata."""

    model_config = OPEN_FOREIGN
    browser_use: bool = Field(default=False, alias="codex/browserUse")


class McpToolCallResult(BaseModel):
    """Represent mcp tool call result."""

    model_config = OPEN_FOREIGN
    content: list[McpToolResultContent | str] | None = None
    is_error: bool = Field(default=False, alias="isError")
    metadata: McpToolResultMetadata | None = Field(default=None, alias="_meta")


class McpToolCallItem(BaseModel):
    """The authoritative completion state for one MCP call.

    The call arguments and result have a tool-specific shape. The outer custom
    tool records own that content. This item owns only the MCP identity and its
    native completion state.
    """

    model_config = OPEN_FOREIGN
    type: Literal["McpToolCall"]
    id: str | None = None
    server: str | None = None
    tool: str | None = None
    status: str | None = None
    arguments: McpToolCallArguments | None = None
    result: McpToolCallResult | None = None


class CoveredItem(BaseModel):
    """An item whose canonical facts come from another native record.

    Open on purpose (OPEN_FOREIGN, module header): the whole point of this
    model is that NOTHING on it is read, only its `type`, so its other
    fields (the very content the other register already delivers) are not
    worth declaring precisely — the shape lives in the response_item models
    that actually read it (items.MessagePayload, items.ReasoningPayload).
    """

    model_config = OPEN_FOREIGN
    type: Literal[
        "UserMessage",
        "AgentMessage",
        "Reasoning",
        "ContextCompaction",
        "Extension",
        "ImageView",
    ]
