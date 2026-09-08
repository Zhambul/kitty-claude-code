# Copyright (c) 2026 Zhambyl Yermagambet
"""Feed entry bodies for skills, questions, and plans."""

from dataclasses import dataclass

from domain.attention import AttentionAnswer, AttentionPrompt
from domain.content import Content
from domain.entry_base import EntryBody, RunState
from domain.ids import AttentionId, SkillId
from domain.outcomes import PlanState


@dataclass(frozen=True)
class SkillStartedBody(EntryBody):
    """Record the start of one skill call."""

    skill_id: SkillId
    name: str
    arguments: Content | None = None


@dataclass(frozen=True)
class SkillFinishedBody(EntryBody):
    """Record the final state of one skill call."""

    skill_id: SkillId
    state: RunState
    result: Content | None = None


@dataclass(frozen=True)
class QuestionAskedBody(EntryBody):
    """Record questions that wait for a person's answer."""

    attention_id: AttentionId
    questions: tuple[AttentionPrompt, ...]


@dataclass(frozen=True)
class QuestionAnsweredBody(EntryBody):
    """Record the answers to one question request."""

    attention_id: AttentionId
    answers: tuple[AttentionAnswer, ...] = ()
    feedback: str | None = None


@dataclass(frozen=True)
class PlanProposedBody(EntryBody):
    """Record a plan that waits for a person's decision."""

    attention_id: AttentionId
    plan: Content


@dataclass(frozen=True)
class PlanResolvedBody(EntryBody):
    """Record a person's decision about a proposed plan."""

    attention_id: AttentionId
    state: PlanState
    feedback: str | None = None
    edited: bool = False
