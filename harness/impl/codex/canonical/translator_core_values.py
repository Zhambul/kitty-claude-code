# Copyright (c) 2026 Zhambyl Yermagambet
"""Split Codex canonical translation."""

from __future__ import annotations

import typing
from types import MappingProxyType

from harness.impl.codex.canonical import translator_dependencies as dependencies
from harness.impl.codex.canonical.translator_identity import (
    CodexToolKind,
    ToolMeaning,
)

SourceIndexValue = typing.TypeVar("SourceIndexValue")


MISSING_NATIVE_VALUE = "<missing>"


CODEX_TOOLS: dependencies.translator_type_dependencies.Mapping[str, ToolMeaning] = MappingProxyType({
    "view_image": ToolMeaning(CodexToolKind.FILE, "ReadImage"),
    "read_mcp_resource": ToolMeaning(CodexToolKind.FILE, "ReadResource"),
    "list_mcp_resources": ToolMeaning(CodexToolKind.IGNORED, "ListResources"),
    "list_mcp_resource_templates": ToolMeaning(
        CodexToolKind.IGNORED,
        "ListResourceTemplates",
    ),
    "image_gen__imagegen": ToolMeaning(CodexToolKind.IGNORED, "GenerateImage"),
    "notify": ToolMeaning(CodexToolKind.IGNORED, "Notify"),
    # Deferred web execution yields a local orchestration handle and Codex
    # later waits on that handle.  The search/fetch call owns the user-visible
    # fact; waiting for its cell has no separate canonical meaning.
    "wait": ToolMeaning(CodexToolKind.IGNORED, "WaitForTool"),
})


GOAL_STATES: dependencies.translator_type_dependencies.Mapping[
    str, dependencies.translator_domain_values.work_state.GoalState,
] = MappingProxyType({
    "active": dependencies.translator_domain_values.work_state.GoalState.ACTIVE,
    "paused": dependencies.translator_domain_values.work_state.GoalState.PAUSED,
    "blocked": dependencies.translator_domain_values.work_state.GoalState.BLOCKED,
    "usageLimited": dependencies.translator_domain_values.work_state.GoalState.USAGE_LIMITED,
    "budgetLimited": dependencies.translator_domain_values.work_state.GoalState.BUDGET_LIMITED,
    "complete": dependencies.translator_domain_values.work_state.GoalState.COMPLETED,
    "cleared": dependencies.translator_domain_values.work_state.GoalState.CLEARED,
})


ACTIVITY_CALLS: dependencies.translator_type_dependencies.Mapping[str, str] = MappingProxyType({
    "started": "spawn_agent",
    "interrupted": "interrupt_agent",
})


FILE_ACTIONS: dependencies.translator_type_dependencies.Mapping[
    str, dependencies.translator_domain_values.outcomes.FileAction,
] = MappingProxyType({
    "add": dependencies.translator_domain_values.outcomes.FileAction.CREATED,
    "delete": dependencies.translator_domain_values.outcomes.FileAction.DELETED,
    "move": dependencies.translator_domain_values.outcomes.FileAction.RENAMED,
    "update": dependencies.translator_domain_values.outcomes.FileAction.UPDATED,
})


FILE_SUBJECT = CodexToolKind.FILE.value


SHELL_SUBJECT = "shell"


SKILL_SUBJECT = "skill"


QUESTION_SUBJECT = "question"


STARTED_PHASE = "started"


FINISHED_PHASE = "finished"


CHANGED_PHASE = "changed"


COMPLETED_STATUS = "completed"


BINARY_READ_MODE = "rb"


BACKWARD_SCAN_CHUNK_BYTES = 65_536
