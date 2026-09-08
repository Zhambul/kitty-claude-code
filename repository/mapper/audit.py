# Copyright (c) 2026 Zhambyl Yermagambet
"""Row DTOs to operational records, and back.

Absorbs the write side's JSON coercion and its content truncation — both used to
sit inside the free functions that also opened the database.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel

from audit.records import ApplicationError, ApplicationErrorRecord, SpawnRecord, StateFileRecord, StreamOpened
from repository.model.audit import ErrorInsertRow, ErrorRow, SpawnInsertRow, StateFileInsertRow, StreamInsertRow

if TYPE_CHECKING:
    from audit.documents import AuditContent

# An audit context is recorded but is not queried. Callers still declare its
# exact shape before this boundary serializes it.
CONTENT_LIMIT = 2000


def text(audit_content: AuditContent) -> str:
    """Any caller value as one string. Never raises: this runs inside `except`.

    Returns:
        Text result.

    """
    if isinstance(audit_content, BaseModel):
        return audit_content.model_dump_json()
    return audit_content or ""


def truncated(audit_content: AuditContent) -> str:
    """Return the truncated.

    Returns:
        Truncated.

    """
    return text(audit_content)[:CONTENT_LIMIT]


def application_error(error_row: ErrorRow) -> ApplicationError:
    """Return the application error.

    Returns:
        Application error.

    """
    return ApplicationError(
        error_id=int(error_row.id),
        timestamp=float(error_row.ts),
        component=error_row.script or "",
        action=error_row.func or "",
        traceback=error_row.traceback or "",
        context=error_row.context or "",
    )


def error_insert_row(application_error_record: ApplicationErrorRecord) -> ErrorInsertRow:
    """Return the error insert row.

    Returns:
        Error insert row.

    """
    return ErrorInsertRow(
        timestamp=application_error_record.timestamp,
        session_id=application_error_record.session_id,
        script=application_error_record.script,
        function=application_error_record.function,
        traceback=application_error_record.traceback,
        context=application_error_record.context,
        process_id=application_error_record.process_id,
    )


def state_file_insert_row(state_file_record: StateFileRecord) -> StateFileInsertRow:
    """Return the state-file insert row.

    Returns:
        State-file insert row.

    """
    return StateFileInsertRow(
        timestamp=state_file_record.timestamp,
        session_id=state_file_record.session_id,
        path=state_file_record.path,
        action=state_file_record.action,
        content=state_file_record.content,
        script=state_file_record.script,
        process_id=state_file_record.process_id,
    )


def spawn_insert_row(spawn_record: SpawnRecord) -> SpawnInsertRow:
    """Return the spawn insert row.

    Returns:
        Spawn insert row.

    """
    return SpawnInsertRow(
        timestamp=spawn_record.timestamp,
        session_id=spawn_record.session_id,
        parent_script=spawn_record.parent_script,
        child_process_id=spawn_record.child_process_id,
        arguments=spawn_record.argv,
        purpose=spawn_record.purpose,
    )


def stream_insert_row(stream_opened: StreamOpened) -> StreamInsertRow:
    """Return the stream insert row.

    Returns:
        Stream insert row.

    """
    return StreamInsertRow(
        session_id=stream_opened.session_id,
        kind=stream_opened.kind,
        agent_id=stream_opened.agent_id,
        task_id=stream_opened.task_id,
        source_path=stream_opened.source_path,
        process_id=stream_opened.process_id,
        started_at=stream_opened.started_at,
    )
