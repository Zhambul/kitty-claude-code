# Copyright (c) 2026 Zhambyl Yermagambet
"""Item javascript records."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harness.impl.codex.canonical import (
    item_patterns,
    record_actor_records,
    record_interaction_records,
    record_response_documents,
    record_terminal_records,
    record_tool_records,
)
from harness.impl.codex.canonical.item_plan_exec import _exec_cmd_from_js, _plan_tasks, _state_tool_action
from harness.impl.codex.canonical.item_response_content import content_text
from harness.impl.codex.canonical.item_tool_arguments import _collaboration_call, _goal_tool, _loose_int_field
from harness.impl.codex.canonical.vocabulary import (
    empty_record,
)

if TYPE_CHECKING:
    from harness.impl.codex.canonical.item_javascript_calls import JavaScriptToolCall
    from harness.impl.codex.ids_session_types import CodexCallId


def _rsp_reasoning(
    reasoning_payload: record_response_documents.ReasoningPayload,
) -> record_terminal_records.RolloutRecord:
    # summary is a list of {"type": "summary_text", "text": …}; it is empty
    # whenever the think was stored as `encrypted_content` instead.
    reasoning_text = content_text(reasoning_payload.summary)
    return record_interaction_records.ThinkRecord(text=reasoning_text) if reasoning_text else empty_record()


def _custom_tool_input(payload: record_response_documents.CustomToolCallPayload) -> str:
    return payload.input if isinstance(payload.input, str) else content_text(payload.input)


def _single_javascript_exec(
    custom_tool_call_payload: record_response_documents.CustomToolCallPayload,
    call_id: CodexCallId,
    javascript: str,
    calls: tuple[JavaScriptToolCall, ...],
) -> record_tool_records.ExecRecord | None:
    command = _exec_cmd_from_js(javascript)
    if not command:
        return None
    metadata = custom_tool_call_payload.internal_chat_message_metadata_passthrough
    arguments = calls[0].arguments if len(calls) == 1 else ""
    return record_tool_records.ExecRecord(
        cmd=command,
        call_id=call_id,
        turn=metadata.turn_id if metadata else None,
        yield_ms=_loose_int_field(arguments, "yield-time_ms"),
        reports_session_id=".session_id" in javascript,
    )


def _javascript_plan_record(
    call_id: CodexCallId,
    javascript: str,
    arguments: str,
) -> record_terminal_records.RolloutRecord:
    tasks = _plan_tasks(arguments)
    if tasks is None:
        tasks = _plan_tasks(javascript)
    if tasks is None:
        return record_actor_records.UnmappedToolRecord(name=item_patterns.UPDATE_PLAN_TOOL_NAME)
    return record_actor_records.TaskListRecord(tasks=tasks, call_id=call_id)


def _javascript_goal_record(
    call_id: CodexCallId, java_script_tool_call: JavaScriptToolCall,
) -> record_terminal_records.RolloutRecord:
    goal = _goal_tool(java_script_tool_call.name, java_script_tool_call.arguments, call_id)
    if goal is None:
        return record_actor_records.UnmappedToolRecord(name=java_script_tool_call.name)
    return goal


def _single_javascript_state_record(
    call_id: CodexCallId,
    javascript: str,
    java_script_tool_call: JavaScriptToolCall,
) -> record_terminal_records.RolloutRecord:
    if java_script_tool_call.name == item_patterns.UPDATE_PLAN_TOOL_NAME:
        return _javascript_plan_record(call_id, javascript, java_script_tool_call.arguments)
    if java_script_tool_call.name in {"create_goal", "get_goal", "update_goal"}:
        return _javascript_goal_record(call_id, java_script_tool_call)
    collaboration = _collaboration_call(
        java_script_tool_call.name, java_script_tool_call.arguments, call_id, javascript=True,
    )
    if collaboration is not None:
        return collaboration
    return record_tool_records.ToolRecord(
        name=java_script_tool_call.name, args=java_script_tool_call.arguments, call_id=call_id,
    )


def _javascript_state_or_tool_action(
    java_script_tool_call: JavaScriptToolCall,
    action_call_id: CodexCallId,
    javascript: str,
) -> (
    record_tool_records.ToolRecord
    | record_actor_records.TaskListRecord
    | record_actor_records.GoalToolRecord
    | record_actor_records.CollaborationCallRecord
):
    action = _state_tool_action(java_script_tool_call.name, java_script_tool_call.arguments, action_call_id)
    if action is None and java_script_tool_call.name == item_patterns.UPDATE_PLAN_TOOL_NAME:
        action = _state_tool_action(java_script_tool_call.name, javascript, action_call_id)
    if action is not None:
        return action
    collaboration = _collaboration_call(
        java_script_tool_call.name, java_script_tool_call.arguments, action_call_id, javascript=True,
    )
    if collaboration is not None:
        return collaboration
    return record_tool_records.ToolRecord(
        name=java_script_tool_call.name, args=java_script_tool_call.arguments, call_id=action_call_id,
    )
