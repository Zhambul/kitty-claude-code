# Copyright (c) 2026 Zhambyl Yermagambet
"""Define question and plan control request values."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from domain.content import StructuredContent
from domain.ids import AttentionId
from harness.models.control_context import ControlTarget
from harness.models.control_enums import AnswerDecision, ControlName


@dataclass(frozen=True)
class AnswerQuestion(ControlTarget):
    """Request an answer or discussion for one question."""

    control_name: ClassVar[ControlName] = ControlName.ANSWER_QUESTION
    attention_id: AttentionId
    decision: AnswerDecision
    answers: StructuredContent | None = None
    discussion: str | None = None


@dataclass(frozen=True)
class ReadPlanChoices(ControlTarget):
    """Request the choices in one plan dialog."""

    control_name: ClassVar[ControlName] = ControlName.READ_PLAN_CHOICES
    attention_id: AttentionId


@dataclass(frozen=True)
class DecidePlan(ControlTarget):
    """Request a decision for one plan."""

    control_name: ClassVar[ControlName] = ControlName.DECIDE_PLAN
    attention_id: AttentionId
    decision: str
    feedback: str | None = None
