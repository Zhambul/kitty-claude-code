# Copyright (c) 2026 Zhambyl Yermagambet
"""Define file, search, web, and worktree entry bodies."""

from __future__ import annotations

from pydantic import BaseModel

from api.common.models.values.content import ContentResponse
from domain.entry_base import FileState
from domain.outcomes import FileAction, WorktreeAction


class FileBodyResponse(BaseModel):
    """Represent a file entry body."""

    path: str
    action: FileAction
    state: FileState
    previous_path: str | None
    line_start: int | None
    line_end: int | None
    lines_added: int | None
    lines_removed: int | None
    content: ContentResponse | None


class SearchBodyResponse(BaseModel):
    """Represent a search entry body."""

    tool: str
    query: ContentResponse
    state: FileState
    result: ContentResponse | None


class WebBodyResponse(BaseModel):
    """Represent a web entry body."""

    url: str | None
    state: FileState
    result: ContentResponse | None


class BrowserBodyResponse(BaseModel):
    """Represent a browser entry body."""

    action: str
    state: FileState
    result: ContentResponse | None


class WorktreeBodyResponse(BaseModel):
    """Represent a worktree entry body."""

    action: WorktreeAction
    state: FileState
    arguments: ContentResponse | None
