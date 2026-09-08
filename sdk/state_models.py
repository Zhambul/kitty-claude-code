# Copyright (c) 2026 Zhambyl Yermagambet
"""Define materialized session state values."""

from __future__ import annotations

from dataclasses import dataclass, field

from api.sessiondata.models import entry as entry_models


@dataclass
class ShellState:
    """Represent one shell state."""

    shell_id: str
    actor_id: str
    turn_id: str | None
    command: str
    execution: str
    started_cursor: int
    output: str = ""
    status: str = ""
    state: str | None = None
    exit_code: int | None = None
    backgrounded: bool = False
    entry_ids: list[str] = field(default_factory=list)


@dataclass
class AssignmentState:
    """Represent one assignment state."""

    assignment_id: str
    owner_actor_id: str
    actor_id: str | None
    turn_id: str | None
    assigned_actor_name: str | None
    requested_prompt: str | None
    started_cursor: int
    state: str | None = None
    result: str = ""
    finished_cursor: int | None = None


@dataclass
class SkillState:
    """Represent one skill state."""

    skill_id: str
    actor_id: str
    turn_id: str | None
    name: str
    arguments: str
    started_cursor: int
    state: str | None = None
    result: str = ""


@dataclass
class QuestionState:
    """Represent one question state."""

    attention_id: str
    actor_id: str
    turn_id: str | None
    questions: tuple[entry_models.QuestionResponse, ...]
    asked_cursor: int
    answers: tuple[entry_models.QuestionAnswerResponse, ...] | None = None
    feedback: str | None = None

    @property
    def pending(self) -> bool:
        """State that needs a response."""
        return self.answers is None


@dataclass
class PlanState:
    """Represent one plan state."""

    attention_id: str
    actor_id: str
    turn_id: str | None
    text: str
    proposed_cursor: int
    state: str | None = None
    feedback: str | None = None
    edited: bool = False

    @property
    def pending(self) -> bool:
        """State that needs a response."""
        return self.state is None


@dataclass
class CompactionState:
    """Represent one compaction state."""

    actor_id: str
    turn_id: str | None
    started_cursor: int
    before_tokens: int | None
    after_tokens: int | None = None
    finished_cursor: int | None = None

    @property
    def finished(self) -> bool:
        """State that has a finish cursor."""
        return self.finished_cursor is not None
