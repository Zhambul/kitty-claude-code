# Copyright (c) 2026 Zhambyl Yermagambet
"""Feed entry bodies for file, search, web, and browser activity."""

from dataclasses import dataclass

from domain.content import Content
from domain.entry_base import EntryBody, FileState
from domain.outcomes import FileAction, WorktreeAction


@dataclass(frozen=True)
class FileBody(EntryBody):
    """Record one completed file operation."""

    path: str
    action: FileAction
    state: FileState
    previous_path: str | None = None
    lines_added: int | None = None
    lines_removed: int | None = None
    content: Content | None = None
    line_start: int | None = None
    line_end: int | None = None


@dataclass(frozen=True)
class SearchBody(EntryBody):
    """Record one completed search operation."""

    tool: str
    query: Content
    state: FileState
    result: Content | None = None


@dataclass(frozen=True)
class WebBody(EntryBody):
    """Record one completed web fetch."""

    url: str | None
    state: FileState
    result: Content | None = None


@dataclass(frozen=True)
class BrowserBody(EntryBody):
    """Record one completed browser operation."""

    action: str
    state: FileState
    result: Content | None = None


@dataclass(frozen=True)
class WorktreeBody(EntryBody):
    """Record a worktree entry or exit."""

    action: WorktreeAction
    state: FileState
    arguments: Content | None = None
