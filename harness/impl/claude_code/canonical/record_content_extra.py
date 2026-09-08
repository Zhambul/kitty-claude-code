# Copyright (c) 2026 Zhambyl Yermagambet
"""Record content extra."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, Field

from harness.impl.claude_code.canonical.record_common import FOREIGN
from harness.impl.claude_code.canonical.record_content_blocks import (
    ImageBlock,
    TextBlock,
    ThinkingBlock,
    ToolResultBlock,
    ToolUseBlock,
)


class FallbackBlock(BaseModel):
    """Represent fallback block.

    A model-swap notice Claude Code injects into `message.content` itself
        (corpus: `{"type": "fallback", "from": "...", "to": "..."}`) — nothing
        here reads it, declared so its shape does not silently drift unnoticed.
        `from` is aliased: it is a Python keyword.
    """

    model_config = FOREIGN
    type: Literal["fallback"] = "fallback"
    from_: str | None = Field(default=None, alias="from")
    to: str | None = None


MessageContentBlock = Annotated[
    TextBlock | ToolUseBlock | ToolResultBlock | ThinkingBlock | ImageBlock | FallbackBlock,
    Field(discriminator="type"),
]
