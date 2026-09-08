# Copyright (c) 2026 Zhambyl Yermagambet
"""The `sessions` table over SQLite."""

from __future__ import annotations

import time
from dataclasses import replace
from typing import TYPE_CHECKING

from core.work_queue import WorkKind
from domain.ids import HarnessName, SessionId
from repository.contract.sessions import SessionRepository
from repository.impl.sqlite import connection as sqlite_connection, rows
from repository.mapper import facts as mapper

if TYPE_CHECKING:
    import sqlite3

    from harness.models.session import (
        Session,
    )
    from harness.registry import HarnessRegistry

_COLUMNS = (
    "session_id, lead_actor_id, harness, harness_session_id, source_reference, "
    "working_directory, project_directory, terminal_window_id, harness_process_id, created_at"
)


class SqliteSessionRepository(SessionRepository):
    """Represent sqlite session repository.

    Constructed with a `HarnessRegistry`, every session it hands out carries
        its `.plugin`. Recorder-side callers construct it without one and get
        plugin-less sessions, which is all a recorder may need.
    """

    def __init__(
        self,
        sqlite_database: sqlite_connection.SqliteDatabase,
        harness_registry: HarnessRegistry | None = None,
    ) -> None:
        """Initialize the object."""
        self.sqlite_database = sqlite_database
        self.harness_registry = harness_registry

    def save(self, harness: HarnessName, session: Session) -> None:
        """Save save."""
        insert_row = mapper.session_insert_row(harness, session, time.time())
        insert_values = (
            insert_row.session_id,
            insert_row.lead_actor_id,
            insert_row.harness,
            insert_row.harness_session_id,
            insert_row.source_reference,
            insert_row.working_directory,
            insert_row.project_directory,
            insert_row.terminal_window_id,
            insert_row.harness_process_id,
            insert_row.created_at,
        )
        with self.sqlite_database.write(WorkKind.SOURCES) as connection:
            connection.execute(
                f"INSERT INTO sessions({_COLUMNS}) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?) "
                "ON CONFLICT(session_id) DO UPDATE SET "
                "  project_directory = COALESCE(sessions.project_directory, excluded.project_directory),"
                "  terminal_window_id = excluded.terminal_window_id,"
                "  harness_process_id = excluded.harness_process_id "
                "WHERE sessions.terminal_window_id IS NOT excluded.terminal_window_id "
                "OR sessions.harness_process_id IS NOT excluded.harness_process_id "
                "OR (sessions.project_directory IS NULL AND excluded.project_directory IS NOT NULL)",
                insert_values,
            )

    def find(self, session_id: SessionId) -> Session | None:
        """Return find.

        Returns:
            Find.

        """
        with self.sqlite_database.read() as connection:
            row = connection.execute("SELECT * FROM sessions WHERE session_id=?", (str(session_id),)).fetchone()
        return None if row is None else self._session(row)

    def watchable(self) -> tuple[Session, ...]:
        """Return the watchable.

        Returns:
            Watchable.

        """
        with self.sqlite_database.read() as connection:
            found = connection.execute(
                "SELECT * FROM sessions WHERE lifecycle = 'running' ORDER BY created_at DESC",
            ).fetchall()
        return tuple(self._session(row) for row in found)

    def _session(self, row: sqlite3.Row) -> Session:
        session = mapper.session(rows.session(row))
        if self.harness_registry is None:
            return session
        return replace(session, plugin=self.harness_registry.plugin(HarnessName(row["harness"])))
