# Copyright (c) 2026 Zhambyl Yermagambet
"""Item output records."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import ValidationError

from harness.impl.codex.canonical import (
    item_patterns,
    record_actor_records,
    record_execution_arguments,
    record_response_documents,
    record_result_documents,
    record_terminal_records,
    record_tool_records,
)
from harness.impl.codex.canonical.item_plan_exec import _exec_cmd_from_js, _exec_output_body
from harness.impl.codex.canonical.item_response_content import _interrupted_output, content_text
from harness.impl.codex.canonical.item_tool_arguments import _loose_int_field
from harness.impl.codex.canonical.vocabulary import (
    empty_record,
)
from harness.impl.codex.ids_session_types import CodexCallId, CodexShellId

if TYPE_CHECKING:
    from harness.impl.codex.ids_conversation_types import CodexTurnId


def _javascript_exec_record(
    call_id: CodexCallId,
    arguments: str,
    javascript: str,
    turn_id: CodexTurnId | None,
) -> record_tool_records.ExecRecord | None:
    command = _exec_cmd_from_js(arguments)
    if not command:
        return None
    return record_tool_records.ExecRecord(
        cmd=command,
        call_id=call_id,
        turn=turn_id,
        yield_ms=_loose_int_field(arguments, "yield_time_ms"),
        reports_session_id=".session_id" in javascript,
    )


def _goal_output_record(body: str) -> record_actor_records.GoalRecord | None:
    try:
        goal_result = record_execution_arguments.GoalToolResultDocument.model_validate_json(body)
    except ValidationError:
        return None
    if goal_result.goal is None:
        return None
    return record_actor_records.GoalRecord(
        objective=goal_result.goal.objective,
        status=goal_result.goal.status,
        reason=goal_result.goal.reason,
    )


def _combined_exec_result(
    command_result: record_result_documents.CombinedToolResult | record_result_documents.CombinedCommandResult,
    call_id: CodexCallId,
) -> record_tool_records.ExecResultRecord:
    process_id = command_result.session_id
    return record_tool_records.ExecResultRecord(
        exit=command_result.exit_code,
        output=command_result.output or "",
        process_id=None if process_id is None else CodexShellId(str(process_id)),
        running=process_id is not None and command_result.exit_code is None,
        call_id=call_id,
    )


def _combined_patch_output(
    combined: record_result_documents.CombinedToolResult, call_id: CodexCallId,
) -> record_terminal_records.RolloutRecord:
    command_result = combined.test
    if command_result is None:
        return empty_record()
    return _combined_exec_result(command_result, call_id)


def _combined_output_record(
    body: str,
    call_id: CodexCallId,
) -> record_terminal_records.RolloutRecord | None:
    try:
        combined = record_result_documents.CombinedToolResult.model_validate_json(body)
    except ValidationError:
        return None
    # An apply_patch-only wrapper returns `{}`; the authoritative FileChange
    # item carries the immutable patch. A combined patch + command wrapper
    # returns both results, so retain only the command result that its matching
    # custom_tool_call opened.
    if combined.patch is not None:
        return _combined_patch_output(combined, call_id)
    if combined.output is not None or combined.session_id is not None or combined.exit_code is not None:
        return _combined_exec_result(combined, call_id)
    if body.strip() == "{}":
        return empty_record()
    return None


def _plain_exec_result(
    output_text: str,
    body: str,
    call_id: CodexCallId,
) -> record_tool_records.ExecResultRecord:
    exit_match = item_patterns.EXECUTION_EXIT_PATTERN.search(output_text[: item_patterns.EXECUTION_EXIT_SCAN_BYTES])
    exit_code: str | int | None = None
    if output_text.startswith("Script failed"):
        exit_code = 1
    if exit_match is not None:
        exit_code = exit_match.group(1)
    return record_tool_records.ExecResultRecord(
        exit=exit_code,
        output=body,
        call_id=call_id,
        interrupted=_interrupted_output(body),
    )


def _rsp_custom_tool_call_output(
    custom_tool_call_output_payload: record_response_documents.CustomToolCallOutputPayload,
) -> record_terminal_records.RolloutRecord | None:
    output_text = (
        custom_tool_call_output_payload.output
        if isinstance(custom_tool_call_output_payload.output, str)
        else content_text(custom_tool_call_output_payload.output)
    )
    body = item_patterns.CITATION_PATTERN.sub("", _exec_output_body(output_text))
    call_id = CodexCallId(custom_tool_call_output_payload.call_id or "")
    goal_record = _goal_output_record(body)
    if goal_record is not None:
        return goal_record
    combined_record = _combined_output_record(body, call_id)
    if combined_record is not None:
        return combined_record
    return _plain_exec_result(output_text, body, call_id)
