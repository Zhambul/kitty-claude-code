# Copyright (c) 2026 Zhambyl Yermagambet
"""Record tool response base."""

from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, Field, RootModel

from harness.impl.claude_code.canonical.record_common import FOREIGN, OPEN_FOREIGN
from harness.impl.claude_code.canonical.record_content_blocks import InnerContentBlock


class PatchHunk(BaseModel):
    """Represent patch hunk.

    One `structuredPatch` hunk of a file-edit tool's response — closed and
        ours to expect exactly (toolcalls.structured_patch reads every field).
    """

    model_config = FOREIGN
    old_start: Annotated[int | None, Field(alias="oldStart")] = None
    old_lines: Annotated[int | None, Field(alias="oldLines")] = None
    new_start: Annotated[int | None, Field(alias="newStart")] = None
    new_lines: Annotated[int | None, Field(alias="newLines")] = None
    lines: list[str] | None = None


class ToolResponseBlocks(RootModel[list[InnerContentBlock | str]]):
    """Represent tool response blocks."""


class ToolResponseImageDimensions(BaseModel):
    """Dimensions Claude records when Read returns an image."""

    model_config = FOREIGN
    original_width: Annotated[int | None, Field(alias="originalWidth")] = None
    original_height: Annotated[int | None, Field(alias="originalHeight")] = None
    display_width: Annotated[int | None, Field(alias="displayWidth")] = None
    display_height: Annotated[int | None, Field(alias="displayHeight")] = None


class ToolResponseFile(BaseModel):
    """The built-in Read tool's text or image result."""

    model_config = FOREIGN
    file_path: Annotated[str | None, Field(alias="filePath")] = None
    content: str | None = None
    num_lines: Annotated[int | None, Field(alias="numLines")] = None
    start_line: Annotated[int | None, Field(alias="startLine")] = None
    total_lines: Annotated[int | None, Field(alias="totalLines")] = None
    truncated_by_token_cap: Annotated[bool | None, Field(alias="truncatedByTokenCap")] = None
    base64: str | None = None
    type: str | None = None
    original_size: Annotated[int | None, Field(alias="originalSize")] = None
    dimensions: ToolResponseImageDimensions | None = None


class WebSearchLink(BaseModel):
    """One readable link in Claude WebSearch's open tool response."""

    model_config = OPEN_FOREIGN
    title: str | None = None
    url: str | None = None


class WebSearchResultSet(BaseModel):
    """The link-bearing member of WebSearch's mixed result list."""

    model_config = OPEN_FOREIGN
    content: list[WebSearchLink] | None = None
