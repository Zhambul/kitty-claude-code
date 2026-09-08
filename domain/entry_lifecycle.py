# Copyright (c) 2026 Zhambyl Yermagambet
"""Feed entry bodies for compaction, assignment, and selection changes."""

from dataclasses import dataclass

from domain.content import Content
from domain.entry_base import EntryBody, RunState
from domain.ids import AssignmentId


@dataclass(frozen=True)
class CompactionStartedBody(EntryBody):
    """Record the token count before context compaction starts."""

    before_tokens: int | None = None


@dataclass(frozen=True)
class CompactionFinishedBody(EntryBody):
    """Record the token counts and retained context after compaction."""

    before_tokens: int | None = None
    after_tokens: int | None = None
    context: Content | None = None


@dataclass(frozen=True)
class AssignmentStartedBody(EntryBody):
    """Record the start of a child-agent assignment."""

    assignment_id: AssignmentId
    assigned_actor_name: str | None = None
    prompt: Content | None = None


@dataclass(frozen=True)
class AssignmentFinishedBody(EntryBody):
    """Record the final state of a child-agent assignment."""

    assignment_id: AssignmentId
    state: RunState = RunState.SUCCEEDED
    result: Content | None = None


@dataclass(frozen=True)
class ModelChangeBody(EntryBody):
    """Record a model selection change."""

    current: str
    previous: str | None = None
    automatic: bool = False


@dataclass(frozen=True)
class EffortChangeBody(EntryBody):
    """Record an effort selection change."""

    current: str
    previous: str | None = None
