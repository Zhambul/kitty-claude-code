# Copyright (c) 2026 Zhambyl Yermagambet
"""Translate Claude source records that need no session state."""

from domain.event_work import TaskListChanged
from domain.records import RecordedTranslationDecision
from harness.impl.claude_code.canonical import records
from harness.impl.claude_code.canonical.otel import translate_otel
from harness.impl.claude_code.canonical.support import event
from harness.impl.claude_code.canonical.tasks import task_file_event
from harness.impl.claude_code.ids import (
    ClaudeCodeTaskId,
    task_id_from_claude_code,
    task_list_id_from_claude_code,
)
from harness.models.raw_event_builders import CanonicalEventDraft
from harness.models.raw_events import RawEvent, TranslationError, TranslationResult


class MalformedTaskListError(TranslationError):
    """Report a Claude task list without its required identity fields."""

    def __init__(self) -> None:
        """Initialize the error."""
        super().__init__("malformed Claude Code task list")


def translate_otel_source(raw_event: RawEvent) -> TranslationResult:
    """Translate an OTEL source record.

    Returns:
        The canonical translation result.

    """
    document = records.OTelMetricsDocument.model_validate_json(raw_event.payload)
    events = translate_otel(raw_event, document)
    if not events:
        return TranslationResult(
            (),
            RecordedTranslationDecision.IGNORED_NONSEMANTIC,
            "OTEL request carries no session usage",
        )
    return TranslationResult(tuple(events), RecordedTranslationDecision.TRANSLATED)


def translate_task_source(raw_event: RawEvent) -> TranslationResult:
    """Translate a task source record.

    Returns:
        The canonical translation result.

    """
    task = records.TaskFile.model_validate_json(raw_event.payload)
    return TranslationResult((task_file_event(raw_event, task),), RecordedTranslationDecision.TRANSLATED)


def translate_task_list_source(raw_event: RawEvent) -> TranslationResult:
    """Translate a task-list source record.

    Returns:
        The canonical translation result.

    Raises:
        MalformedTaskListError: If the source record is malformed.

    """
    task_list = records.TaskListDocument.model_validate_json(raw_event.payload)
    if task_list.list_id is None or task_list.task_ids is None:
        raise MalformedTaskListError
    payload = TaskListChanged(
        task_list_id_from_claude_code(task_list.list_id),
        tuple(task_id_from_claude_code(ClaudeCodeTaskId(task_id)) for task_id in task_list.task_ids),
    )
    canonical = event(raw_event, CanonicalEventDraft("task_list", raw_event.source_position, "changed", payload))
    return TranslationResult((canonical,), RecordedTranslationDecision.TRANSLATED)
