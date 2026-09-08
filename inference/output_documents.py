# Copyright (c) 2026 Zhambyl Yermagambet
"""Declare accepted documents from inference command output."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

PERMISSIVE_MODEL_CONFIG = ConfigDict(extra="allow")


class TitleDocument(BaseModel):
    """Hold a structured model title."""

    model_config = PERMISSIVE_MODEL_CONFIG
    title: str


class CodexItem(BaseModel):
    """Hold the text of one Codex output item."""

    model_config = PERMISSIVE_MODEL_CONFIG
    text: str | None = None


class CodexEvent(BaseModel):
    """Hold one Codex output event."""

    model_config = PERMISSIVE_MODEL_CONFIG
    event_item: CodexItem | None = Field(default=None, alias="item")


class ClaudeOutput(BaseModel):
    """Hold the structured and plain forms of Claude output."""

    model_config = PERMISSIVE_MODEL_CONFIG
    structured_output: TitleDocument | None = None
    result: str | None = None
