# Copyright (c) 2026 Zhambyl Yermagambet
"""Record documents."""

from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, Field, RootModel

from harness.impl.claude_code.canonical.record_common import FOREIGN, OPEN_FOREIGN
from harness.impl.claude_code.canonical.record_otel_base import OTelResourceMetrics
from harness.impl.claude_code.ids import (
    ClaudeCodeTaskListId,
)


class OTelMetricsDocument(BaseModel):
    """Represent otel metrics document."""

    model_config = OPEN_FOREIGN
    resource_metrics: Annotated[list[OTelResourceMetrics], Field(alias="resourceMetrics")] = Field(default_factory=list)


class LaunchSelectionDocument(BaseModel):
    """Represent launch selection document.

    The launch observation the hook gateway records from the CLI's
        inherited environment (`--model`/`--effort`) — closed, ours to define on
        both ends (hooks/gateway.py writes it, launch_selections reads it).
    """

    model_config = FOREIGN
    model: str | None = None
    effort: str | None = None


class AgentMetaFile(BaseModel):
    """Represent agent meta file.

    A subagent's `agent-<id>.meta.json` sidecar — corpus-observed (this
        machine's own sidecars, 2026-08-22): every field any of them has ever
        carried, though `description`/`taskKind` are the only two read.
    """

    model_config = FOREIGN
    agent_type: Annotated[str | None, Field(alias="agentType")] = None
    color: str | None = None
    custom_agent_type: Annotated[str | None, Field(alias="customAgentType")] = None
    description: str | None = None
    is_fork: Annotated[bool | None, Field(alias="isFork")] = None
    model: str | None = None
    name: str | None = None
    parent_agent_id: Annotated[str | None, Field(alias="parentAgentId")] = None
    permission_mode: Annotated[str | None, Field(alias="permissionMode")] = None
    plan_mode_required: Annotated[bool | None, Field(alias="planModeRequired")] = None
    spawn_depth: Annotated[int | None, Field(alias="spawnDepth")] = None
    stopped_by_user: Annotated[bool | None, Field(alias="stoppedByUser")] = None
    task_kind: Annotated[str | None, Field(alias="taskKind")] = None
    team_name: Annotated[str | None, Field(alias="teamName")] = None
    tool_use_id: Annotated[str | None, Field(alias="toolUseId")] = None
    worktree_branch: Annotated[str | None, Field(alias="worktreeBranch")] = None
    worktree_cleanly_removed: Annotated[bool | None, Field(alias="worktreeCleanlyRemoved")] = None
    worktree_path: Annotated[str | None, Field(alias="worktreePath")] = None


class TaskFile(BaseModel):
    """Represent task file.

    One `~/.claude/tasks/session-<id>/<task-id>.json` snapshot — corpus-
        observed (this machine's own task files, 2026-08-22): every session task
        Claude Code has ever written carries exactly these eight fields.
    """

    model_config = FOREIGN
    id: str | int | None = None
    subject: str | None = None
    description: str | None = None
    active_form: Annotated[str | None, Field(alias="activeForm")] = None
    status: str | None = None
    owner: str | None = None
    blocks: list[str | int] | None = None
    blocked_by: Annotated[list[str | int] | None, Field(alias="blockedBy")] = None


class TaskListDocument(BaseModel):
    """Represent task list document.

    The `task_list` raw event's payload — OURS on both ends
        (ClaudeTaskRawEventSource writes it, ClaudeCanonicalTranslator reads it).
    """

    model_config = FOREIGN
    list_id: ClaudeCodeTaskListId | None = None
    task_ids: list[str] | None = None


class TaskSnapshot(RootModel[tuple[TaskFile, ...]]):
    """Represent task snapshot."""
