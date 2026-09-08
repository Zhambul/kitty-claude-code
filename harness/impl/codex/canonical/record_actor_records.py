# Copyright (c) 2026 Zhambyl Yermagambet
"""Own actor records models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from harness.impl.codex.canonical.record_collaboration_registry import CollaborationArguments
from harness.impl.codex.canonical.record_plan_arguments import PlanTask
from harness.impl.codex.canonical.record_tool_records import ExecRecord, StdinRecord, ToolRecord
from harness.impl.codex.ids_session_types import CodexActorId, CodexCallId


@dataclass(frozen=True, kw_only=True)
class ActorActivityRecord:
    """Represent actor activity record."""

    kind: Literal["actor_activity"] = "actor_activity"
    activity: str
    actor_id: CodexActorId
    call_id: CodexCallId
    turn: str
    at: float | None


@dataclass(frozen=True, kw_only=True)
class CollaborationCallRecord:
    """Represent collaboration call record."""

    kind: Literal["collaboration_call"] = "collaboration_call"
    name: str
    args: CollaborationArguments
    call_id: CodexCallId


@dataclass(frozen=True, kw_only=True)
class TaskListRecord:
    """Represent task list record."""

    kind: Literal["task_list"] = "task_list"
    tasks: tuple[PlanTask, ...]
    call_id: CodexCallId


@dataclass(frozen=True, kw_only=True)
class GoalRecord:
    """Represent goal record."""

    kind: Literal["goal"] = "goal"
    objective: str | None
    status: str | None
    reason: str | None


@dataclass(frozen=True, kw_only=True)
class GoalToolRecord:
    """Represent goal tool record."""

    kind: Literal["goal_tool"] = "goal_tool"
    call_id: CodexCallId
    name: str
    objective: str | None = None
    status: str | None = None
    reason: str | None = None


@dataclass(frozen=True, kw_only=True)
class ToolBatchRecord:
    """Represent tool batch record."""

    kind: Literal["tool_batch"] = "tool_batch"
    call_id: CodexCallId
    ordered_results: bool = False
    actions: tuple[
        ExecRecord | StdinRecord | ToolRecord | TaskListRecord | GoalToolRecord | CollaborationCallRecord,
        ...,
    ]


@dataclass(frozen=True, kw_only=True)
class UnmappedToolRecord:
    """Represent unmapped tool record."""

    kind: Literal["unmapped_tool"] = "unmapped_tool"
    name: str
