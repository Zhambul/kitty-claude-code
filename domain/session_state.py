# Copyright (c) 2026 Zhambyl Yermagambet
"""Stored aggregate state for one coding session."""

from dataclasses import dataclass

from domain.actor_state import ActorFacts
from domain.ids import ActorId, HarnessName, SessionId, TaskId
from domain.lifecycle import LifecycleState
from domain.references import AccountReference
from domain.stored import STORED
from domain.work_state import GoalState, TaskState


@dataclass(frozen=True)
class SessionGoal:
    """Hold the current user goal for a session."""

    __pydantic_config__ = STORED

    objective: str | None
    state: GoalState
    reason: str | None


@dataclass(frozen=True)
class SessionTask:
    """Hold one task in a session task list."""

    __pydantic_config__ = STORED

    task_id: TaskId
    subject: str
    description: str | None
    state: TaskState
    owner_actor_id: ActorId | None


@dataclass(frozen=True)
class SessionFacts:
    """Hold the stored aggregate fields for one session."""

    __pydantic_config__ = STORED

    session_id: SessionId
    harness: HarnessName
    state: LifecycleState
    working_directory: str
    started_at: float | None
    lead_actor_id: ActorId
    title: str | None = None
    finished_at: float | None = None
    account: AccountReference | None = None
    goal: SessionGoal | None = None
    tasks: tuple[SessionTask, ...] = ()
    continued_from: SessionId | None = None
    prompt_title_internal: str | None = None
    custom_title_internal: str | None = None
    automatic_title_internal: str | None = None
    summary_title_internal: str | None = None
    task_order_internal: tuple[TaskId, ...] = ()


@dataclass(frozen=True)
class SessionData:
    """Hold one session aggregate and its stream cursor."""

    session: SessionFacts
    actors: tuple[ActorFacts, ...]
    cursor: int
    last_activity_at: float | None = None
