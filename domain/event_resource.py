# Copyright (c) 2026 Zhambyl Yermagambet
"""Canonical payloads for file, search, web, and tool activity."""

from dataclasses import dataclass

from domain.content import Content
from domain.event_base import EventPayload
from domain.ids import SkillId
from domain.outcomes import FileAction, Outcome, WorktreeAction


@dataclass(frozen=True)
class FileAccessed(EventPayload):
    """Record one completed file operation."""

    path: str
    action: FileAction
    outcome: Outcome
    previous_path: str | None = None
    line_start: int | None = None
    line_end: int | None = None
    lines_added: int | None = None
    lines_removed: int | None = None
    unified_diff: str | None = None
    content: Content | None = None


@dataclass(frozen=True)
class SearchPerformed(EventPayload):
    """Record one search and the matches that it returned."""

    tool: str
    query: Content
    result: Content | None
    outcome: Outcome


@dataclass(frozen=True)
class SkillStarted(EventPayload):
    """Record the start of one skill call."""

    skill_id: SkillId
    name: str
    arguments: Content | None


@dataclass(frozen=True)
class SkillFinished(EventPayload):
    """Record the final outcome of one skill call."""

    skill_id: SkillId
    outcome: Outcome
    result: Content | None


@dataclass(frozen=True)
class WebFetched(EventPayload):
    """Record one web fetch and the page that it returned."""

    url: str | None
    result: Content | None
    outcome: Outcome


@dataclass(frozen=True)
class BrowserInteracted(EventPayload):
    """Record one browser action and its observation."""

    action: str
    result: Content | None
    outcome: Outcome


@dataclass(frozen=True)
class WorktreeChanged(EventPayload):
    """Record a worktree entry or exit."""

    action: WorktreeAction
    arguments: Content | None
    outcome: Outcome
