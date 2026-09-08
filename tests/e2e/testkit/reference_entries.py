# Copyright (c) 2026 Zhambyl Yermagambet
"""Define E2E references for observed session entries."""

from __future__ import annotations

from dataclasses import dataclass

from sdk.client import SessionRef


@dataclass(frozen=True)
class ActorMessageRef:
    """Represent one message from one actor to another."""

    session: SessionRef
    entry_id: str
    sender_actor_id: str
    recipient_actor_id: str
    text: str


@dataclass(frozen=True)
class FileOperationRef:
    """Represent one file operation entry."""

    session: SessionRef
    entry_id: str
    actor_id: str


@dataclass(frozen=True)
class SearchRef:
    """Represent one search entry."""

    session: SessionRef
    entry_id: str


@dataclass(frozen=True)
class WebFetchRef:
    """Represent one web fetch entry."""

    session: SessionRef
    entry_id: str


@dataclass(frozen=True)
class ReasoningTraceRef:
    """Represent a set of reasoning entries."""

    session: SessionRef
    actor_id: str
    entry_ids: tuple[str, ...]


@dataclass(frozen=True)
class WorktreeChangeRef:
    """Represent one worktree change entry."""

    session: SessionRef
    entry_id: str


@dataclass(frozen=True)
class SkillRef:
    """Represent one skill entry."""

    session: SessionRef
    skill_id: str
