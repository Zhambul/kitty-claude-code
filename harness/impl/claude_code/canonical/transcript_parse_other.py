# Copyright (c) 2026 Zhambyl Yermagambet
"""Parse Claude attachment and queue transcript records."""

from harness.impl.claude_code.canonical import records
from harness.impl.claude_code.canonical.transcript_model_activity import (
    BackgroundCommandCompletedTranscriptRecord,
    GoalTranscriptRecord,
)
from harness.impl.claude_code.canonical.transcript_model_core import PromptTranscriptRecord, TranscriptKind
from harness.impl.claude_code.canonical.transcript_model_notifications import (
    ActorAssignmentFinishedTranscriptRecord,
    MonitorEndedTranscriptRecord,
    MonitorEventTranscriptRecord,
    TranscriptRecord,
)
from harness.impl.claude_code.canonical.transcript_notifications import (
    COMPLETED_STATUS,
    TASK_NOTIFICATION as _TASK_NOTE,
    task_notification as _task_notification,
)


def _parse_attachment_record(line: str) -> TranscriptRecord | None:
    """Parse one native attachment record.

    Returns:
        The parsed record, or None for an unused attachment.

    """
    attachment_record = records.AttachmentRecord[records.AttachmentHeader].model_validate_json(line)
    attachment_type = None if attachment_record.attachment is None else attachment_record.attachment.type
    if attachment_type == "goal_status":
        return _goal_attachment_record(line)
    if attachment_type == "queued_command":
        return _queued_attachment_record(line)
    return None


def _goal_attachment_record(line: str) -> GoalTranscriptRecord | None:
    goal_attachment = records.AttachmentRecord[records.GoalStatusAttachment].model_validate_json(line).attachment
    if goal_attachment is None:
        return None
    objective = str(goal_attachment.condition or "").strip()
    if not objective:
        return None
    goal_state = COMPLETED_STATUS if goal_attachment.met is True else "active"
    reason = str(goal_attachment.reason or "").strip() or None
    return GoalTranscriptRecord(objective, goal_state, reason)


def _queued_attachment_record(line: str) -> PromptTranscriptRecord | None:
    queued_attachment = records.AttachmentRecord[records.QueuedCommandAttachment].model_validate_json(line).attachment
    if queued_attachment is None:
        return None
    if queued_attachment.command_mode != TranscriptKind.PROMPT.value:
        return None
    return PromptTranscriptRecord(queued_attachment.prompt or "", queued=True)


def _parse_queue_record(line: str) -> TranscriptRecord | None:
    """Parse one native queue operation.

    Returns:
        The parsed notification, or None for an unused operation.

    """
    queue_record = records.QueueOperationRecord.model_validate_json(line)
    is_task_notification = (
        queue_record.operation == "enqueue"
        and isinstance(queue_record.content, str)
        and _TASK_NOTE.search(queue_record.content) is not None
    )
    if not is_task_notification or not isinstance(queue_record.content, str):
        return None
    notification = _task_notification(queue_record.content)
    supported_types = (
        BackgroundCommandCompletedTranscriptRecord,
        MonitorEventTranscriptRecord,
        MonitorEndedTranscriptRecord,
        ActorAssignmentFinishedTranscriptRecord,
    )
    return notification if isinstance(notification, supported_types) else None
