# Copyright (c) 2026 Zhambyl Yermagambet
"""Item function calls."""

from __future__ import annotations

from harness.impl.codex.canonical import (
    record_actor_records,
    record_collaboration_registry,
    record_context_records,
    record_execution_arguments,
    record_interaction_records,
    record_response_documents,
    record_terminal_records,
    record_tool_records,
)
from harness.impl.codex.canonical.item_execution_calls import (
    _call_exec,
    _javascript_tool_batch,
    _single_javascript_record,
    _stdin_record,
)
from harness.impl.codex.canonical.item_javascript_calls import JavaScriptToolCall, js_tool_calls
from harness.impl.codex.canonical.item_javascript_records import _custom_tool_input, _single_javascript_exec
from harness.impl.codex.canonical.vocabulary import (
    empty_record,
)
from harness.impl.codex.ids_session_types import CodexCallId


def _exec_custom_tool_call(
    payload: record_response_documents.CustomToolCallPayload, call_id: CodexCallId,
) -> record_terminal_records.RolloutRecord:
    javascript = _custom_tool_input(payload)
    calls = js_tool_calls(javascript)
    if len(calls) > 1:
        return _javascript_tool_batch(payload, call_id, javascript, calls)
    exec_record = _single_javascript_exec(payload, call_id, javascript, calls)
    if exec_record is not None:
        return exec_record
    call = calls[0] if calls else JavaScriptToolCall("", "")
    return _single_javascript_record(call_id, javascript, call)


def _rsp_custom_tool_call(
    custom_tool_call_payload: record_response_documents.CustomToolCallPayload,
) -> record_terminal_records.RolloutRecord | None:
    call_id = CodexCallId(custom_tool_call_payload.call_id or "")
    if custom_tool_call_payload.name == "exec":
        return _exec_custom_tool_call(custom_tool_call_payload, call_id)
    if custom_tool_call_payload.name == "apply_patch":
        return record_interaction_records.PatchCallRecord(
            patch=_custom_tool_input(custom_tool_call_payload), call_id=call_id,
        )
    return None


def _call_stdin(
    function_call_payload: record_response_documents.FunctionCallPayload,
    stdin_arguments: record_execution_arguments.StdinArguments,
) -> record_tool_records.StdinRecord:
    return _stdin_record(CodexCallId(function_call_payload.call_id or ""), stdin_arguments)


def _call_ask(
    function_call_payload: record_response_documents.FunctionCallPayload,
    ask_arguments: record_execution_arguments.AskArguments,
) -> record_interaction_records.AskRecord | None:
    questions = tuple(
        record_context_records.AskQuestionRecord(
            id=question.id or "",
            header=question.header or "",
            question=question.question or "",
            options=tuple(
                record_context_records.AskOptionRecord(label=option.label or "", description=option.description or "")
                for option in (question.options or ())
            ),
        )
        for question in (ask_arguments.questions or ())
    )
    # call_id rides along so a presenter can pair the ask with its
    # function_call_output ANSWER without re-reading the raw payload.
    call_id = CodexCallId(function_call_payload.call_id or "")
    return record_interaction_records.AskRecord(call_id=call_id, questions=questions) if questions else None


def _collaboration_function_record(
    payload: record_response_documents.FunctionCallPayload,
    name: str,
    arguments: str | None,
) -> record_terminal_records.RolloutRecord:
    try:
        collaboration_name = record_collaboration_registry.CollaborationCallName(name)
    except ValueError:
        collaboration_name = None
    collaboration_arguments = (
        record_collaboration_registry.COLLABORATION_ARGUMENTS.get(collaboration_name) if collaboration_name else None
    )
    if collaboration_arguments is not None:
        return record_actor_records.CollaborationCallRecord(
            name=name,
            args=collaboration_arguments.model_validate_json(
                arguments or collaboration_arguments().model_dump_json(),
            ),
            call_id=CodexCallId(payload.call_id or ""),
        )
    # An unlisted name is None, so a new codex tool degrades to "not rendered"
    # rather than to an exception.
    return record_actor_records.UnmappedToolRecord(name=name)


def _other_function_call(
    function_call_payload: record_response_documents.FunctionCallPayload,
    name: str,
    arguments: str | None,
) -> record_terminal_records.RolloutRecord:
    if name == "wait":
        # Deferred custom-tool orchestration. The originating tool owns the
        # semantic fact; waiting for its cell only schedules transport work.
        return empty_record()
    if name == "run":
        # The pre-code-mode web connector exposed the same request grammar as a
        # direct function named `run`; current Codex calls `tools.web__run`.
        return record_tool_records.ToolRecord(
            name="web__run",
            args=arguments or "{}",
            call_id=CodexCallId(function_call_payload.call_id or ""),
        )
    return _collaboration_function_record(function_call_payload, name, arguments)


def _rsp_function_call(
    function_call_payload: record_response_documents.FunctionCallPayload,
) -> record_terminal_records.RolloutRecord | None:
    name = function_call_payload.name or ""
    arguments = function_call_payload.arguments
    # `shell` is the pre-0.1x spelling of `exec_command` (same {command: [...]}
    # shape) and still turns up in older rollouts.
    if name in {"exec_command", "shell"}:
        return _call_exec(
            function_call_payload,
            record_execution_arguments.ExecArguments.model_validate_json(
                arguments or record_execution_arguments.ExecArguments().model_dump_json(),
            ),
        )
    if name == "write_stdin":
        return _call_stdin(
            function_call_payload,
            record_execution_arguments.StdinArguments.model_validate_json(
                arguments or record_execution_arguments.StdinArguments().model_dump_json(),
            ),
        )
    if name == "request_user_input":
        return _call_ask(
            function_call_payload,
            record_execution_arguments.AskArguments.model_validate_json(
                arguments or record_execution_arguments.AskArguments().model_dump_json(),
            ),
        )
    return _other_function_call(function_call_payload, name, arguments)
