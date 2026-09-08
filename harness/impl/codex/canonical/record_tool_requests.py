# Copyright (c) 2026 Zhambyl Yermagambet
"""Own tool requests models."""

from __future__ import annotations

from pydantic import BaseModel, Field

from harness.impl.codex.canonical.record_config import OPEN_FOREIGN


class ToolRequest(BaseModel):
    """Represent tool request."""

    model_config = OPEN_FOREIGN
    short_query: str | None = Field(default=None, alias="q")
    query: str | None = None
    url: str | None = None
    location: str | None = None
    ticker: str | None = None
    utc_offset: str | None = None
    team: str | None = None
    fn: str | None = None
    reference: str | None = Field(default=None, alias="ref_id")


class CodexToolArguments(BaseModel):
    """Represent codex tool arguments."""

    model_config = OPEN_FOREIGN
    search_query: list[ToolRequest] | None = None
    image_query: list[ToolRequest] | None = None
    weather: list[ToolRequest] | None = None
    finance: list[ToolRequest] | None = None
    sports: list[ToolRequest] | None = None
    time: list[ToolRequest] | None = None
    open: list[ToolRequest] | None = None
    click: list[ToolRequest] | None = None
    find: list[ToolRequest] | None = None
    screenshot: list[ToolRequest] | None = None
    query: str | None = None
    url: str | None = None
    path: str | None = None
    file_path: str | None = None
    uri: str | None = None
