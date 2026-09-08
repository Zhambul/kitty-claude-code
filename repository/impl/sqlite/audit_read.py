# Copyright (c) 2026 Zhambyl Yermagambet
"""Read audit records without opening the database for writes."""

from __future__ import annotations

from typing import TYPE_CHECKING

from domain.ids import SessionId
from repository.contract.audit import AuditReadRepository
from repository.impl.sqlite import connection as sqlite_connection, rows
from repository.mapper import audit as mapper

if TYPE_CHECKING:
    from collections.abc import Mapping

    from audit.records import ApplicationError


class SqliteAuditReadRepository(AuditReadRepository):
    """Represent sqlite audit read repository."""

    def __init__(self, sqlite_database: sqlite_connection.SqliteDatabase) -> None:
        """Initialize the object."""
        self.sqlite_database = sqlite_database

    def errors_for_session(self, session_id: SessionId) -> tuple[ApplicationError, ...]:
        """Return the errors for session.

        Returns:
            Errors for session.

        """
        if not self.sqlite_database.exists():
            return ()
        with self.sqlite_database.read() as connection:
            found = connection.execute(
                "SELECT * FROM errors WHERE session_id=? ORDER BY id",
                (str(session_id),),
            ).fetchall()
        return tuple(mapper.application_error(rows.error(row)) for row in found)

    def error_counts(self) -> Mapping[SessionId, int]:
        """Return the error counts.

        Returns:
            Error counts.

        """
        if not self.sqlite_database.exists():
            return {}
        with self.sqlite_database.read() as connection:
            found = connection.execute(
                "SELECT session_id, COUNT(*) AS error_count FROM errors WHERE session_id != '' GROUP BY session_id",
            ).fetchall()
        counts = {}
        for row in found:
            counts[SessionId(row["session_id"])] = int(row["error_count"])
        return counts
