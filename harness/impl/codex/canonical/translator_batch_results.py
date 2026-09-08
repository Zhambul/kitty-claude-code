# Copyright (c) 2026 Zhambyl Yermagambet
"""Match explicitly ordered command results to their calls."""

import re

from pydantic import ValidationError

from harness.impl.codex.canonical.item_javascript_calls import JavaScriptToolCall
from harness.impl.codex.canonical.record_actor_records import ToolBatchRecord
from harness.impl.codex.canonical.record_result_documents import CombinedCommandResult
from harness.impl.codex.canonical.record_tool_records import ExecRecord, ExecResultRecord
from harness.impl.codex.ids_session_types import CodexShellId

type ProcessResult = bool | ExecResultRecord


def ordered_command_results(javascript: str, calls: tuple[JavaScriptToolCall, ...]) -> bool:
    """Check that each command prints its result before the next command.

    Returns:
        True only for direct, sequential command prints.

    """
    patterns: list[str] = []
    for call in calls:
        if call.name not in {"exec_command", "write_stdin"}:
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
    if len(lines) != len(tool_batch_record.actions):
        return ()
    matched: list[ExecResultRecord] = []
    for action, line in zip(tool_batch_record.actions, lines, strict=True):
        try:
            command = CombinedCommandResult.model_validate_json(line)
        except ValidationError:
            return ()
        if all(
            field is None for field in (command.output, command.session_id, command.exit_code)
        ):
            return ()
        matched.append(ExecResultRecord(
            call_id=action.call_id,
            exit=command.exit_code,
            output=command.output or "",
            process_id=None if command.session_id is None else CodexShellId(str(command.session_id)),
            running=command.session_id is not None and command.exit_code is None,
            ts=exec_result_record.ts,
        ))
    return tuple(matched)


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
