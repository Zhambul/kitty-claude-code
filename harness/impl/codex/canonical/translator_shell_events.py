# Copyright (c) 2026 Zhambyl Yermagambet
"""Split Codex canonical translation."""

from __future__ import annotations

import os

from harness.impl.codex.canonical import translator_dependencies as dependencies
from harness.impl.codex.canonical.translator_core_values import (
    COMPLETED_STATUS,
    FINISHED_PHASE,
    SHELL_SUBJECT,
)
from harness.impl.codex.canonical.translator_state_models import (
    CommandCompletion,
    RecordSource,
    ResolvedCompletedShell,
    ShellResultContext,
)

SHELL_COMMAND_MINIMUM_PARTS = 3


def shell_event(
    shell_result_context: ShellResultContext,
    phase: str,
    payload: dependencies.translator_type_dependencies.event_base.EventPayload,
) -> dependencies.translator_type_dependencies.event_base.CanonicalEvent[
    dependencies.translator_type_dependencies.event_base.EventPayload
]:
    """Build a shell event from its result context.

    Returns:
        The canonical event with the source time and turn identity.

    """
    return dependencies.translator_codex_dependencies.support.event(
        shell_result_context.source.raw_event,
        dependencies.translator_service_dependencies.CanonicalEventDraft(
            SHELL_SUBJECT,
            str(shell_result_context.shell_id),
            phase,
            payload,
            turn_id=shell_result_context.turn_id,
            occurred_at=shell_result_context.source.occurred_at,
        ),
    )


def shell_progress_event(
    shell_result_context: ShellResultContext,
    output: str,
) -> dependencies.translator_type_dependencies.event_base.CanonicalEvent[
    dependencies.translator_type_dependencies.event_base.EventPayload
]:
    """Build an output event for the shell.

    Returns:
        A shell progress event ordered by its raw source position.

    """
    ordinal = int(shell_result_context.source.raw_event.source_position)
    payload = dependencies.translator_domain_events.event_shell.ShellProgressed(
        shell_result_context.shell_id,
        ordinal,
        dependencies.translator_domain_values.outcomes.ProgressStream.OUTPUT,
        dependencies.translator_codex_dependencies.support.content(output),
        dependencies.translator_domain_values.outcomes.OutputMode.APPEND,
    )
    return shell_event(shell_result_context, f"progress:{ordinal}", payload)


def command_completion(
    record_source: RecordSource,
    record: dependencies.record_canonical_namespaces.record_tool_records.CommandCompletedRecord,
) -> CommandCompletion:
    """Resolve the source and turn of a completed command.

    Returns:
        The command record with its resolved source path and optional turn.

    """
    turn_id = (
        dependencies.translator_id_dependencies.ids_conversation.turn_id_from_codex(record.turn)
        if record.turn
        else None
    )
    return CommandCompletion(record_source, record, os.path.realpath(record_source.raw_event.source_name), turn_id)


def completed_command(native_command: tuple[str, ...]) -> str:
    """Extract command text from the native argument list.

    Returns:
        The shell command argument, or all arguments joined with spaces.

    """
    if (
        len(native_command) >= SHELL_COMMAND_MINIMUM_PARTS
        and native_command[-2] in {"-c", "-lc"}
    ):
        return native_command[-1]
    return " ".join(native_command)


def completed_shell_event(
    command_completion: CommandCompletion,
    shell_id: dependencies.translator_type_dependencies.ids.ShellId,
    phase: str,
    payload: dependencies.translator_type_dependencies.event_base.EventPayload,
) -> dependencies.translator_type_dependencies.event_base.CanonicalEvent[
    dependencies.translator_type_dependencies.event_base.EventPayload
]:
    """Build an event from a completed command context.

    Returns:
        The canonical shell event for the supplied phase and payload.

    """
    return dependencies.translator_codex_dependencies.support.event(
        command_completion.source.raw_event,
        dependencies.translator_service_dependencies.CanonicalEventDraft(
            SHELL_SUBJECT,
            str(shell_id),
            phase,
            payload,
            turn_id=command_completion.turn_id,
            occurred_at=command_completion.source.occurred_at,
        ),
    )


def completed_shell_events(
    command_completion: CommandCompletion,
    resolved_completed_shell: ResolvedCompletedShell,
    process_exit_code: int | None,
    outcome: dependencies.translator_domain_values.outcomes.Outcome,
) -> list[
    dependencies.translator_type_dependencies.event_base.CanonicalEvent[
        dependencies.translator_type_dependencies.event_base.EventPayload
    ]
]:
    """Build the events for a completed shell.

    Returns:
        The finish event, preceded by the start event if one was supplied.

    """
    payload = dependencies.translator_domain_events.event_shell.ShellFinished(
        resolved_completed_shell.shell_id,
        outcome,
        dependencies.translator_codex_dependencies.support.content(command_completion.record.output),
        process_exit_code,
    )
    events = [completed_shell_event(command_completion, resolved_completed_shell.shell_id, FINISHED_PHASE, payload)]
    if resolved_completed_shell.started is not None:
        events.insert(0, resolved_completed_shell.started)
    return events


def browser_outcome(
    record: dependencies.record_canonical_namespaces.record_tool_records.McpToolCompletedRecord,
) -> dependencies.translator_domain_values.outcomes.Outcome:
    """Read the outcome of a browser tool result.

    Returns:
        Failure for an error result, or success for a completed result.

    Raises:
        TranslationError: If the status is not recognized.

    """
    if record.status == "failed" or record.result_is_error:
        return dependencies.translator_domain_values.outcomes.Outcome.FAILED
    if record.status == COMPLETED_STATUS:
        return dependencies.translator_domain_values.outcomes.Outcome.SUCCEEDED
    msg = f"unknown Codex browser interaction state: {record.status!r}"
    raise dependencies.translator_service_dependencies.raw_events.TranslationError(
        msg,
    )
