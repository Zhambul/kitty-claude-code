# Copyright (c) 2026 Zhambyl Yermagambet
"""Item execution calls."""

from __future__ import annotations

import ast
import re
from typing import TYPE_CHECKING

from pydantic import ValidationError

from harness.impl.codex.canonical import (
    record_actor_records,
    record_execution_arguments,
    record_response_documents,
    record_terminal_records,
    record_tool_records,
    translator_batch_results,
)
from harness.impl.codex.canonical.item_javascript_records import (
    _javascript_state_or_tool_action,
    _single_javascript_state_record,
)
from harness.impl.codex.canonical.item_output_records import _javascript_exec_record
from harness.impl.codex.canonical.vocabulary import (
    empty_record,
)
from harness.impl.codex.ids_session_types import CodexCallId, CodexShellId

if TYPE_CHECKING:
    from harness.impl.codex.canonical.item_javascript_calls import JavaScriptToolCall
    from harness.impl.codex.ids_conversation_types import CodexTurnId


def _call_exec(
    function_call_payload: record_response_documents.FunctionCallPayload,
    exec_arguments: record_execution_arguments.ExecArguments,
) -> record_tool_records.ExecRecord | None:
    command = exec_arguments.cmd or exec_arguments.command or ""
    if isinstance(command, list):
        command = " ".join(str(command_part) for command_part in command)
    if not command:
        return None
    metadata = function_call_payload.internal_chat_message_metadata_passthrough
    return record_tool_records.ExecRecord(
        cmd=command,
        call_id=CodexCallId(function_call_payload.call_id or ""),
        turn=metadata.turn_id if metadata else None,
    )


def _loose_stdin_arguments(arguments: str) -> record_execution_arguments.StdinArguments | None:
    process_match = re.search(r'(?:^|[,{])\s*["\']?session_id["\']?\s*:\s*(\d+)', arguments)
    if process_match is None:
        return None
    chars_match = re.search(
        r'(?:^|[,{])\s*["\']?chars["\']?\s*:\s*("(?:[^"\\]|\\.)*")',
        arguments,
    )
    chars = ast.literal_eval(chars_match.group(1)) if chars_match else ""
    return record_execution_arguments.StdinArguments(session_id=CodexShellId(process_match.group(1)), chars=chars)


def _stdin_arguments(
    arguments: record_execution_arguments.StdinArguments | str,
) -> record_execution_arguments.StdinArguments | None:
    if isinstance(arguments, record_execution_arguments.StdinArguments):
        return arguments
    try:
        return record_execution_arguments.StdinArguments.model_validate_json(arguments)
    except ValidationError:
        return _loose_stdin_arguments(arguments)


def _stdin_record(
    call_id: CodexCallId, arguments: record_execution_arguments.StdinArguments | str,
) -> record_tool_records.StdinRecord:
    """Normalize only the measured write_stdin argument shape.

    Current custom-tool rollouts contain either JSON (validated strictly by
    StdinArguments) or a JavaScript object literal with unquoted keys, which
    this parser does not interpret; it extracts the two fields that define the
    continuation with a targeted regex instead.

    Returns:
        The stdin record.

    """
    fields = _stdin_arguments(arguments)
    if fields is None:
        return record_tool_records.StdinRecord(text="", call_id=call_id, process_id=CodexShellId(""))
    process_id = fields.session_id
    return record_tool_records.StdinRecord(
        text=fields.chars or "",
        call_id=call_id,
        process_id=CodexShellId("") if process_id is None else CodexShellId(str(process_id)),
    )


def _single_javascript_record(
    call_id: CodexCallId,
    javascript: str,
    java_script_tool_call: JavaScriptToolCall,
) -> record_terminal_records.RolloutRecord:
    if not java_script_tool_call.name or java_script_tool_call.name in {"exec", "apply_patch"}:
        return empty_record()
    if java_script_tool_call.name == "write_stdin":
        return _stdin_record(call_id, java_script_tool_call.arguments)
    if java_script_tool_call.name == "exec_command":
        return record_terminal_records.CoveredItemRecord()
    return _single_javascript_state_record(call_id, javascript, java_script_tool_call)


def _javascript_batch_action(
    java_script_tool_call: JavaScriptToolCall,
    index: int,
    batch_call_id: CodexCallId,
    javascript: str,
    turn_id: CodexTurnId | None,
) -> (
    record_tool_records.ExecRecord
    | record_tool_records.StdinRecord
    | record_tool_records.ToolRecord
    | record_actor_records.TaskListRecord
    | record_actor_records.GoalToolRecord
    | record_actor_records.CollaborationCallRecord
    | None
):
    if java_script_tool_call.name in {"apply_patch", "exec"}:
        return None
    action_call_id = CodexCallId(f"{batch_call_id}:{index}")
    if java_script_tool_call.name == "exec_command":
        return _javascript_exec_record(action_call_id, java_script_tool_call.arguments, javascript, turn_id)
    if java_script_tool_call.name == "write_stdin":
        continuation = _stdin_record(action_call_id, java_script_tool_call.arguments)
        return continuation if continuation.process_id else None
    return _javascript_state_or_tool_action(java_script_tool_call, action_call_id, javascript)


def _javascript_tool_batch(
    custom_tool_call_payload: record_response_documents.CustomToolCallPayload,
    call_id: CodexCallId,
    javascript: str,
    calls: tuple[JavaScriptToolCall, ...],
) -> record_terminal_records.RolloutRecord:
    actions: list[
        record_tool_records.ExecRecord
        | record_tool_records.StdinRecord
        | record_tool_records.ToolRecord
        | record_actor_records.TaskListRecord
        | record_actor_records.GoalToolRecord
        | record_actor_records.CollaborationCallRecord
    ] = []
    metadata = custom_tool_call_payload.internal_chat_message_metadata_passthrough
    for index, call in enumerate(calls, start=1):
        action = _javascript_batch_action(
            call,
            index,
            call_id,
            javascript,
            metadata.turn_id if metadata else None,
        )
        if action is not None:
            actions.append(action)
    return record_actor_records.ToolBatchRecord(
        call_id=call_id,
        actions=tuple(actions),
        ordered_results=(
            len(actions) == len(calls) and translator_batch_results.ordered_command_results(javascript, calls)
        ),
    ) if actions else empty_record()
