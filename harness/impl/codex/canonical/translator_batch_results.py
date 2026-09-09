# Copyright (c) 2026 Zhambyl Yermagambet
"""Match explicitly ordered command results to their calls."""

import re

from harness.impl.codex.canonical.item_javascript_calls import JavaScriptToolCall
from harness.impl.codex.canonical.record_actor_records import ToolBatchRecord
from harness.impl.codex.canonical.record_result_documents import CombinedCommandResult
from harness.impl.codex.canonical.record_tool_records import ExecRecord, ExecResultRecord
from harness.impl.codex.ids_session_types import CodexCallId, CodexShellId

type ProcessResult = bool | ExecResultRecord


def command_result_order(
    call_id: CodexCallId, calls: tuple[JavaScriptToolCall, ...],
) -> tuple[CodexCallId | None, ...]:
    """Keep the result slot for each printed call.

    Returns:
        Call identities, with an empty slot for patch output.

    """
    return tuple(
        None if call.name == "apply_patch" else CodexCallId(f"{call_id}:{index}")
        for index, call in enumerate(calls, start=1)
    )


def ordered_command_results(javascript: str, calls: tuple[JavaScriptToolCall, ...]) -> bool:
    """Check that each command prints its result before the next command.

    Returns:
        True only for direct, sequential command prints.

    """
    patterns: list[str] = []
    for call in calls:
        if call.name not in {"exec_command", "write_stdin", "apply_patch"}:
            return False
        patterns.append(
            r"\s*text\s*\(\s*await\s+tools\."
            + re.escape(call.name)
            + r"\s*\(\s*"
            + re.escape(call.arguments)
            + r"\s*\)\s*\)\s*;?\s*",
        )
    return re.fullmatch("".join(patterns), javascript) is not None


def command_results(
    tool_batch_record: ToolBatchRecord, exec_result_record: ExecResultRecord,
) -> tuple[ExecResultRecord, ...]:
    """Read one result per direct, sequential command print.

    Returns:
        Matched results, or no results if the output order is not known.

    """
    if not tool_batch_record.ordered_results:
        return ()
    lines = exec_result_record.output.splitlines()
    result_order = tool_batch_record.result_order or tuple(action.call_id for action in tool_batch_record.actions)
    if len(lines) != len(result_order):
        return ()
    matched: list[ExecResultRecord] = []
    for call_id, line in zip(result_order, lines, strict=True):
        if call_id is None:
            continue
        try:
            matched.append(_command_result(call_id, line, exec_result_record.ts))
        except ValueError:
            return ()
    return tuple(matched)


def _command_result(call_id: CodexCallId, line: str, timestamp: str | None) -> ExecResultRecord:
    command = CombinedCommandResult.model_validate_json(line)
    if all(
        field is None for field in (command.output, command.session_id, command.exit_code)
    ):
        msg = "Printed output is not a command result"
        raise ValueError(msg)
    return ExecResultRecord(
        call_id=call_id,
        exit=command.exit_code,
        output=command.output or "",
        process_id=None if command.session_id is None else CodexShellId(str(command.session_id)),
        running=command.session_id is not None and command.exit_code is None,
        ts=timestamp,
    )


def process_call(
    tool_batch_record: ToolBatchRecord, process_result: ProcessResult, process_id: CodexShellId,
) -> ExecRecord | None:
    """Find the command that opened a recorded process.

    Returns:
        The command, or None if the result cannot identify it.

    """
    if isinstance(process_result, bool):
        return None
    matched = command_results(tool_batch_record, process_result)
    if not matched:
        return None
    for action, result in zip(tool_batch_record.actions, matched, strict=True):
        if isinstance(action, ExecRecord) and result.running and result.process_id == process_id:
            return action
    return None
