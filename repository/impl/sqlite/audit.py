# Copyright (c) 2026 Zhambyl Yermagambet
"""The audit database over SQLite.

The write side NEVER RAISES. It is called from `except` blocks in short-lived
hook processes, and an auditor that can fail takes down the thing it exists to
explain. Every method swallows storage failure, and the whole repository is a
no-op when the audit is switched off.

The read side opens the file read-only.
"""

from __future__ import annotations

import os
import sqlite3
import time
from dataclasses import astuple
from typing import TYPE_CHECKING

from audit.records import (
    ApplicationErrorRecord,
    SpawnRecord,
    StateFileRecord,
    StreamHandle,
    StreamOpened,
)
from repository.contract.audit import (
    AuditWriteRepository,
)
from repository.mapper import audit as mapper

if TYPE_CHECKING:
    from repository.impl.sqlite import connection as sqlite_connection
    from repository.model.sql import SqlValues


def audit_enabled() -> bool:
    """Return the audit enabled.

    Returns:
        Audit enabled.

    """
    return os.environ.get("BAQYLAU_AUDIT", "1") != "0"


class SqliteAuditWriteRepository(AuditWriteRepository):
    """Represent sqlite audit write repository."""

    def __init__(self, sqlite_database: sqlite_connection.SqliteDatabase) -> None:
        """Initialize the object."""
        self.sqlite_database = sqlite_database

    def record_error(self, application_error_record: ApplicationErrorRecord) -> None:
        """Record error."""
        self._insert(
            "INSERT INTO errors(ts, session_id, script, func, traceback, context, pid) VALUES(?,?,?,?,?,?,?)",
            astuple(mapper.error_insert_row(application_error_record)),
        )

    def record_state_file(self, state_file_record: StateFileRecord) -> None:
        """Record state file."""
        self._insert(
            "INSERT INTO state_files(ts, session_id, path, action, content, script, pid) VALUES(?,?,?,?,?,?,?)",
            astuple(mapper.state_file_insert_row(state_file_record)),
        )

    def record_spawn(self, spawn_record: SpawnRecord) -> None:
        """Record spawn."""
        self._insert(
            "INSERT INTO spawns(ts, session_id, parent_script, child_pid, argv, purpose) VALUES(?,?,?,?,?,?)",
            astuple(mapper.spawn_insert_row(spawn_record)),
        )

    def open_stream(self, stream_opened: StreamOpened) -> StreamHandle | None:
        """Open stream.

        Returns:
            The stream handle.

        """
        if not audit_enabled():
            return None
        try:
            with self.sqlite_database.write() as connection:
                cursor = connection.execute(
                    "INSERT INTO streams(session_id, kind, agent_id, task_id, src_path, "
                    "pid, started_at) VALUES(?,?,?,?,?,?,?)",
                    astuple(mapper.stream_insert_row(stream_opened)),
                )
                # lastrowid is Optional in the DB-API: it is set after this
                # INSERT, but int() on the None branch would raise, and this
                # method is already declared to answer None when it cannot open.
                return StreamHandle(cursor.lastrowid) if cursor.lastrowid else None
        except (sqlite3.Error, OSError):
            return None

    def close_stream(
        self,
        stream_handle: StreamHandle | None,
        end_reason: str,
        lines_emitted: int | None,
    ) -> None:
        """Close stream."""
        if stream_handle is None:
            return
        self._insert(
            "UPDATE streams SET ended_at=?, end_reason=?, lines_emitted=? WHERE id=?",
            (time.time(), end_reason, lines_emitted, stream_handle.stream_id),
        )

    def _insert(self, statement: str, statement_parameters: SqlValues) -> None:
        if not audit_enabled():
            return
        try:
            with self.sqlite_database.write() as connection:
                connection.execute(statement, statement_parameters)
        except (sqlite3.Error, OSError):
            # A broken auditor must never take down the thing it exists to
            # explain. There is nowhere left to report this to.
            return
