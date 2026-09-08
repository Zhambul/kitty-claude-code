# Copyright (c) 2026 Zhambyl Yermagambet
"""Canonical payloads for tasks, goals, questions, and plans."""

from dataclasses import dataclass

from domain.attention import AttentionAnswer, AttentionPrompt
from domain.content import Content
from domain.event_base import EventPayload
from domain.ids import ActorId, AttentionId, TaskId, TaskListId
from domain.outcomes import PlanState
from domain.work_state import GoalState, TaskState


@dataclass(frozen=True)
class TaskChanged(EventPayload):
    """Record the current state and owner of one task."""

    task_id: TaskId
    subject: str
    description: str | None
    state: TaskState
    owner_actor_id: ActorId | None


@dataclass(frozen=True)
class TaskListChanged(EventPayload):
    """Record the ordered membership of a task list."""

    list_id: TaskListId
    task_ids: tuple[TaskId, ...]


@dataclass(frozen=True)
class GoalChanged(EventPayload):
    """Record the current state of a session goal."""

    objective: str | None
    state: GoalState
    reason: str | None


@dataclass(frozen=True)
class QuestionAsked(EventPayload):
    """Record questions that wait for a person's answer."""

    attention_id: AttentionId
    questions: tuple[AttentionPrompt, ...]


@dataclass(frozen=True)
class QuestionAnswered(EventPayload):
    """Record a person's answers to one question request."""

    attention_id: AttentionId
    answers: tuple[AttentionAnswer, ...]
    feedback: str | None


@dataclass(frozen=True)
class PlanProposed(EventPayload):
    """Record a plan that waits for a person's decision."""

    attention_id: AttentionId
    plan: Content


@dataclass(frozen=True)
class PlanResolved(EventPayload):
    """Record a person's decision about a proposed plan."""

    attention_id: AttentionId
    state: PlanState
    feedback: str | None
    edited: bool
