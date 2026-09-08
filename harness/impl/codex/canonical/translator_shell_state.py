# Copyright (c) 2026 Zhambyl Yermagambet
"""Split Codex canonical translation."""

from __future__ import annotations

import os
import re

from harness.impl.codex.canonical import translator_dependencies as dependencies
from harness.impl.codex.canonical.translator_state_models import (
    RecordSource,
    ShellProcess,
    ShellResultContext,
)

_REPORTED_PROCESS_ID = re.compile(
    r"(?:session(?:_id)?\s*[:=]?\s*)?(\d+)",
    re.IGNORECASE,
)


def exec_outcome(
    record: dependencies.record_canonical_namespaces.record_tool_records.ExecResultRecord,
) -> dependencies.translator_domain_values.outcomes.Outcome:
    """Read the outcome of a native execution result.

    Returns:
        Cancelled for an interrupt, failed for a nonzero exit, or succeeded.

    """
    if record.interrupted:
        return dependencies.translator_domain_values.outcomes.Outcome.CANCELLED
    exit_code = dependencies.translator_codex_dependencies.support.exit_code(record.exit)
    if exit_code in {None, 0}:
        return dependencies.translator_domain_values.outcomes.Outcome.SUCCEEDED
    return dependencies.translator_domain_values.outcomes.Outcome.FAILED


def shell_result_context(
    record_source: RecordSource,
    call_id: dependencies.translator_id_dependencies.ids_session_types.CodexCallId,
    call_record: dependencies.record_canonical_namespaces.record_tool_records.ExecRecord,
) -> ShellResultContext:
    """Collect the source, shell, and turn identities for a result.

    Returns:
        The context used to build shell result events.

    """
    turn_id = (
        dependencies.translator_id_dependencies.ids_conversation.turn_id_from_codex(call_record.turn)
        if call_record.turn
        else None
    )
    return ShellResultContext(
        record_source,
        os.path.realpath(record_source.raw_event.source_name),
        dependencies.translator_id_dependencies.ids_session.shell_id_from_codex_call(call_id),
        turn_id,
    )


def shell_process(
    call_record: dependencies.record_canonical_namespaces.record_tool_records.ExecRecord,
    record: dependencies.record_canonical_namespaces.record_tool_records.ExecResultRecord,
) -> ShellProcess:
    """Read process identity and yield state from a native result.

    Returns:
        The exit code, process identifier, and identified yield state.

    """
    reported = _REPORTED_PROCESS_ID.fullmatch(record.output.strip()) if call_record.reports_session_id else None
    process_id = record.process_id or _reported_process_id(reported)
    yielded_with_identity = _yielded_with_identity(call_record, record, process_id, reported)
    return ShellProcess(
        dependencies.translator_codex_dependencies.support.exit_code(record.exit), process_id, yielded_with_identity,
    )


def _reported_process_id(
    reported: re.Match[str] | None,
) -> dependencies.translator_id_dependencies.ids_session_types.CodexShellId:
    process_id = "" if reported is None else reported.group(1)
    return dependencies.translator_id_dependencies.ids_session_types.CodexShellId(process_id)


def _yielded_with_identity(
    call_record: dependencies.record_canonical_namespaces.record_tool_records.ExecRecord,
    record: dependencies.record_canonical_namespaces.record_tool_records.ExecResultRecord,
    process_id: dependencies.translator_id_dependencies.ids_session_types.CodexShellId,
    reported: re.Match[str] | None,
) -> bool:
    has_yield = call_record.yield_ms is not None and record.exit is None
    return has_yield and bool(process_id) and reported is not None


def is_empty_yield(
    call_record: dependencies.record_canonical_namespaces.record_tool_records.ExecRecord,
    record: dependencies.record_canonical_namespaces.record_tool_records.ExecResultRecord,
) -> bool:
    """Check for a timed yield without output or an exit code.

    Returns:
        True if the result is an empty yield.

    """
    return call_record.yield_ms is not None and record.exit is None and not record.output


def shell_is_running(
    call_record: dependencies.record_canonical_namespaces.record_tool_records.ExecRecord,
    record: dependencies.record_canonical_namespaces.record_tool_records.ExecResultRecord,
    shell_process: ShellProcess,
) -> bool:
    """Check whether native result data keeps the shell active.

    Returns:
        True for a running result or a supported yield form.

    """
    return record.running or is_empty_yield(call_record, record) or shell_process.yielded_with_identity
