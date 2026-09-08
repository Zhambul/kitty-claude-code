# Copyright (c) 2026 Zhambyl Yermagambet
"""Item plan exec."""

from __future__ import annotations

import ast
from typing import TYPE_CHECKING

from pydantic import ValidationError

from harness.impl.codex.canonical import item_patterns, record_actor_records, record_plan_arguments
from harness.impl.codex.canonical.item_tool_arguments import _goal_tool, _next_plan_item_start, _plan_task_values

if TYPE_CHECKING:
    import re

    from harness.impl.codex.ids_session_types import CodexCallId


def _javascript_plan_task(
    arguments: str,
    matches: list[re.Match[str]],
    index: int,
    step_match: re.Match[str],
) -> record_plan_arguments.PlanTask | None:
    item_end = _next_plan_item_start(arguments, matches, index)
    status_match = item_patterns.PLAN_STATUS_PATTERN.search(arguments, step_match.end(), item_end)
    if status_match is None:
        return None
    try:
        step, status = _plan_task_values(step_match, status_match)
    except (SyntaxError, ValueError):
        return None
    return record_plan_arguments.PlanTask(step=step, status=status)


def _javascript_plan_tasks(arguments: str) -> tuple[record_plan_arguments.PlanTask, ...] | None:
    matches = list(item_patterns.PLAN_STEP_PATTERN.finditer(arguments or ""))
    if not matches:
        return None
    tasks: list[record_plan_arguments.PlanTask] = []
    for index, step_match in enumerate(matches):
        task = _javascript_plan_task(arguments, matches, index, step_match)
        if task is None:
            return None
        tasks.append(task)
    return tuple(tasks)


def _plan_tasks(arguments: str) -> tuple[record_plan_arguments.PlanTask, ...] | None:
    """Return the plan tasks.

    A `update_plan` JS call's steps, JSON or JS-literal — see PlanArguments
        (records.py): the args are usually JSON even inside the JS snippet, but a
        JS object literal with unquoted keys falls back to a targeted scan, the
        same duality _stdin_record below reads for `write_stdin`.

    Returns:
        Plan tasks.

    """
    try:
        return tuple(record_plan_arguments.PlanArguments.model_validate_json(arguments).plan or ())
    except ValidationError:
        return _javascript_plan_tasks(arguments)


def _state_tool_action(
    name: str,
    arguments: str,
    call_id: CodexCallId,
) -> record_actor_records.TaskListRecord | record_actor_records.GoalToolRecord | None:
    if name == item_patterns.UPDATE_PLAN_TOOL_NAME:
        tasks = _plan_tasks(arguments)
        return None if tasks is None else record_actor_records.TaskListRecord(tasks=tasks, call_id=call_id)
    if name in {"create_goal", "get_goal", "update_goal"}:
        return _goal_tool(name, arguments, call_id)
    return None


def _decoded_javascript_command(raw_command: str) -> str:
    try:
        decoded_command = ast.literal_eval(raw_command)
    except (SyntaxError, ValueError):
        clean_command = raw_command.strip()
        if clean_command[:1] in "\"'`":
            return clean_command[1:-1]
        return clean_command
    if isinstance(decoded_command, list):
        return " ".join(str(command_part) for command_part in decoded_command)
    return str(decoded_command)


def _exec_cmd_from_js(javascript: str) -> str:
    """Return the exec cmd from js.

    The SHELL command out of a `custom_tool_call` name=exec JS `input`, or ''
        when the call is not a shell one — `tools.exec_command({cmd:…})` yields its
        cmd, anything else is a different tool and belongs to js_tool_calls above (the
        `tool` record), not to a command block.

    Returns:
        Exec cmd from js.

    """
    command_match = item_patterns.JAVASCRIPT_COMMAND_PATTERN.search(javascript or "")
    if not command_match:
        return ""
    raw = command_match.group(1)
    if raw.startswith("`") and "${" in raw:
        # Runtime interpolation cannot be recovered faithfully. A native
        # CommandExecution item later supplies the resolved command.
        return ""
    return _decoded_javascript_command(raw)


def _exec_output_body(output_text: str) -> str:
    r"""Return the exec output body.

    A custom-exec output stripped of codex's `…Output:\\\\\\\\n` status preamble, so
        the block body is the command's real output (uniform with a Claude command);
        the whole text is still what the exit is scanned from.

    Returns:
        Exec output body.

    """
    marker_index = output_text.find(item_patterns.OUTPUT_MARKER)
    if marker_index >= 0:
        return output_text[marker_index + len(item_patterns.OUTPUT_MARKER) :].lstrip("\n")
    return "" if output_text.endswith(item_patterns.OUTPUT_MARKER.rstrip("\n")) else output_text
