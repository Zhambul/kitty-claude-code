# Copyright (c) 2026 Zhambyl Yermagambet
"""Own task records models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True, kw_only=True)
class TaskStartedRecord:
    """Represent task started record."""

    kind: Literal["task_started"] = "task_started"
    at: str | int | float | None
    turn: str
    ts: str | None = None


@dataclass(frozen=True, kw_only=True)
class TaskCompleteRecord:
    """Represent task complete record."""

    kind: Literal["task_complete"] = "task_complete"
    at: str | int | float | None
    turn: str
    last: str
    ts: str | None = None


@dataclass(frozen=True, kw_only=True)
class TurnAbortedRecord:
    """Represent turn aborted record."""

    kind: Literal["turn_aborted"] = "turn_aborted"
    turn: str


@dataclass(frozen=True, kw_only=True)
class PromptRecord:
    """Represent prompt record."""

    kind: Literal["prompt"] = "prompt"
    text: str


@dataclass(frozen=True, kw_only=True)
class SkillRecord:
    """Represent skill record."""

    kind: Literal["skill"] = "skill"
    name: str
    output: str
    turn: str


@dataclass(frozen=True, kw_only=True)
class ReasoningRecord:
    """Represent reasoning record."""

    kind: Literal["reasoning"] = "reasoning"
    text: str


@dataclass(frozen=True, kw_only=True)
class MessageRecord:
    """Represent message record."""

    kind: Literal["message"] = "message"
    text: str
    phase: str
    ts: str | None = None
