# Copyright (c) 2026 Zhambyl Yermagambet
"""Record content blocks."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

from harness.impl.claude_code.canonical.record_common import FOREIGN, OPEN_FOREIGN, ImageSource
from harness.impl.claude_code.canonical.record_questions import ToolArguments
from harness.impl.claude_code.ids import (
    ClaudeCodeCallId,
)


class TextBlock(BaseModel):
    """Represent text block."""

    model_config = FOREIGN
    type: Literal["text"] = "text"
    text: str | None = None


class DirectCaller(BaseModel):
    """Claude Code's typed marker for a tool call made by the lead agent."""

    model_config = FOREIGN
    type: Literal["direct"] = "direct"


class ToolUseBlock(BaseModel):
    """Represent tool use block."""

    model_config = FOREIGN
    type: Literal["tool_use"] = "tool_use"
    id: str | None = None
    name: str | None = None
    caller: DirectCaller | None = None
    # The tool's own arguments — a genuinely open, per-tool shape (module
    # header); read generically here and validated against the specific
    # tool's ARGUMENTS model only once TOOL_KINDS has named it (toolcalls.py).
    input: ToolArguments | None = None


class InnerContentBlock(BaseModel):
    """Represent inner content block.

    One block of a tool_result's OWN `content` — GENUINELY open (module
        header): it is whatever the tool that answered chose to put there, a
        Claude Code built-in's plain text/image or an MCP tool's own shape.
        Declared as far as reality allows: `text`/`tool_name`/`source` are the
        three fields transcript.result_text() reads (the corpus's `text`,
        `tool_reference`, `image` block kinds); anything else rides along unread.
    """

    model_config = OPEN_FOREIGN
    type: str | None = None
    text: str | None = None
    tool_name: str | None = None
    source: ImageSource | None = None


class ToolResultBlock(BaseModel):
    """Represent tool result block."""

    model_config = FOREIGN
    type: Literal["tool_result"] = "tool_result"
    tool_use_id: ClaudeCodeCallId | None = None
    is_error: bool | None = None
    content: str | list[InnerContentBlock | str] | None = None


class ThinkingBlock(BaseModel):
    """Represent thinking block."""

    model_config = FOREIGN
    type: Literal["thinking"] = "thinking"
    thinking: str | None = None
    signature: str | None = None


class ImageBlock(BaseModel):
    """Represent image block."""

    model_config = FOREIGN
    type: Literal["image"] = "image"
    source: ImageSource | None = None
