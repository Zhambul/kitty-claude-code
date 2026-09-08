# Copyright (c) 2026 Zhambyl Yermagambet
"""Item tool arguments."""

from __future__ import annotations

import ast
import re
from typing import TYPE_CHECKING

from pydantic import ValidationError

from harness.impl.codex.canonical import (
    item_patterns,
    record_actor_records,
    record_collaboration_arguments,
    record_collaboration_registry,
    record_plan_arguments,
)

if TYPE_CHECKING:
    from harness.impl.codex.ids_session_types import CodexCallId


def _loose_string_field(arguments: str, field: str) -> str | None:
    match = re.search(
        rf"""["']?{field}["']?\s*:\s*("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')""",
        arguments,
    )
    if match is None:
        return None
    try:
        return str(ast.literal_eval(match.group(1)))
    except (SyntaxError, ValueError):
        return None


def _loose_int_field(arguments: str, field: str) -> int | None:
    for spelling in (field, field.replace("-", "_")):
        match = re.search(
            rf"""["']?{re.escape(spelling)}["']?\s*:\s*(\d+)""",
            arguments,
        )
        if match is not None:
            return int(match.group(1))
    return None


def _goal_tool(
    name: str,
    arguments: str,
    call_id: CodexCallId,
) -> record_actor_records.GoalToolRecord | None:
    try:
        parsed = record_plan_arguments.GoalArguments.model_validate_json(arguments)
    except ValidationError:
        parsed = record_plan_arguments.GoalArguments(
            objective=_loose_string_field(arguments, "objective"),
            status=_loose_string_field(arguments, "status"),
            reason=_loose_string_field(arguments, "reason"),
        )
    return record_actor_records.GoalToolRecord(
        call_id=call_id,
        name=name,
        objective=parsed.objective,
        status=parsed.status,
        reason=parsed.reason,
    )


def _collaboration_name(native_name: str) -> record_collaboration_registry.CollaborationCallName | None:
    name = item_patterns.COLLABORATION_TOOL_PREFIX.sub("", native_name, count=1)
    try:
        return record_collaboration_registry.CollaborationCallName(name)
    except ValueError:
        return None


def _collaboration_call(
    native_name: str,
    arguments: str,
    call_id: CodexCallId,
    *,
    javascript: bool = False,
) -> record_actor_records.CollaborationCallRecord | None:
    name = _collaboration_name(native_name)
    argument_model = None if name is None else record_collaboration_registry.COLLABORATION_ARGUMENTS.get(name)
    if name is None or argument_model is None:
        return None
    try:
        parsed: record_collaboration_registry.CollaborationArguments = argument_model.model_validate_json(
            arguments or argument_model().model_dump_json(),
        )
    except ValidationError:
        if not javascript:
            raise
        if name == record_collaboration_registry.CollaborationCallName.SEND_MESSAGE:
            parsed = record_collaboration_arguments.SendMessageArguments(
                message=_loose_string_field(arguments, "message"),
                content=_loose_string_field(arguments, "content"),
                target=_loose_string_field(arguments, "target"),
            )
        else:
            parsed = argument_model()
    return record_actor_records.CollaborationCallRecord(name=name.value, args=parsed, call_id=call_id)


def _plan_task_values(
    step_match: re.Match[str],
    status_match: re.Match[str],
) -> tuple[str, str]:
    step_value = step_match.group(1)
    status_value = status_match.group(1)
    return ast.literal_eval(step_value), ast.literal_eval(status_value)


def _next_plan_item_start(arguments: str, matches: list[re.Match[str]], index: int) -> int:
    next_index = index + 1
    if next_index < len(matches):
        return matches[next_index].start()
    return len(arguments)
