# Copyright (c) 2026 Zhambyl Yermagambet
"""Own terminal records models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from harness.impl.codex.canonical.record_actor_records import (
    ActorActivityRecord,
    CollaborationCallRecord,
    GoalRecord,
    GoalToolRecord,
    TaskListRecord,
    ToolBatchRecord,
    UnmappedToolRecord,
)
from harness.impl.codex.canonical.record_context_records import (
    CompactRecord,
    PatchRecord,
    TurnContextRecord,
    UsageRecord,
)
from harness.impl.codex.canonical.record_interaction_records import (
    AskRecord,
    ChatRecord,
    CompactBoundaryRecord,
    PatchCallRecord,
    PlanRecord,
    SettingsRecord,
    ThinkRecord,
)
from harness.impl.codex.canonical.record_task_records import (
    MessageRecord,
    PromptRecord,
    ReasoningRecord,
    SkillRecord,
    TaskCompleteRecord,
    TaskStartedRecord,
    TurnAbortedRecord,
)
from harness.impl.codex.canonical.record_tool_records import (
    CommandCompletedRecord,
    ExecRecord,
    ExecResultRecord,
    McpToolCompletedRecord,
    SearchRecord,
    StdinRecord,
    ToolRecord,
)


@dataclass(frozen=True, kw_only=True)
class BadRecord:
    """Represent bad record."""

    kind: Literal["bad"] = "bad"
    raw: str


@dataclass(frozen=True, kw_only=True)
class WorldStateRecord:
    """Represent world state record."""

    kind: Literal["world_state"] = "world_state"


@dataclass(frozen=True, kw_only=True)
class CoveredItemRecord:
    """Represent covered item record."""

    kind: Literal["covered_item"] = "covered_item"


@dataclass(frozen=True, kw_only=True)
class EmptyRecord:
    """Represent empty record."""

    kind: Literal["empty"] = "empty"


type RolloutRecord = (
    TurnContextRecord
    | UsageRecord
    | PatchRecord
    | CompactRecord
    | TaskStartedRecord
    | TaskCompleteRecord
    | TurnAbortedRecord
    | PromptRecord
    | SkillRecord
    | ReasoningRecord
    | MessageRecord
    | SearchRecord
    | ExecRecord
    | ExecResultRecord
    | StdinRecord
    | CommandCompletedRecord
    | McpToolCompletedRecord
    | ChatRecord
    | ThinkRecord
    | PatchCallRecord
    | AskRecord
    | PlanRecord
    | SettingsRecord
    | CompactBoundaryRecord
    | ToolRecord
    | ActorActivityRecord
    | CollaborationCallRecord
    | TaskListRecord
    | GoalRecord
    | GoalToolRecord
    | ToolBatchRecord
    | UnmappedToolRecord
    | BadRecord
    | WorldStateRecord
    | CoveredItemRecord
    | EmptyRecord
)
