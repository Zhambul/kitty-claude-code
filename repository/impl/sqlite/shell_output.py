# Copyright (c) 2026 Zhambyl Yermagambet
"""The follow list over SQLite.

Nothing here touches the filesystem: `remove_expired` returns what it deleted so
the caller unlinks. Deleting a user's file used to be a side effect of listing
the rows.
"""

from __future__ import annotations

from dataclasses import astuple
from typing import TYPE_CHECKING

from core.work_queue import WorkKind
from repository.contract.shell_output import ShellOutputLifecycle, ShellOutputRepository
from repository.impl.sqlite import rows
from repository.mapper import facts as mapper

if TYPE_CHECKING:
    from domain.ids import SessionId, ShellId
    from domain.shells import ShellOutputFollowing
    from repository.impl.sqlite.connection import SqliteDatabase

_COLUMNS = (
    "session_id, shell_id, harness, actor_id, parent_actor_id, "
    "source_path, chunk_source_type, delete_source, initial_size, "
    "initial_modified_at, wait_for_source_change, until, state, created_at"
)


class ShellOutputTransitions(ShellOutputLifecycle):
    """Apply lifecycle changes to stored shell output."""

    sqlite_database: SqliteDatabase

    def mark_shell_finished(self, session_id: SessionId, shell_id: ShellId) -> None:
        """Mark output that waits for shell completion as finishing."""
        with self.sqlite_database.write(WorkKind.SOURCES) as connection:
            connection.execute(
                "UPDATE shell_output SET state='finishing' "
                "WHERE session_id=? AND shell_id=? AND until='shell_finished'",
                (str(session_id), str(shell_id)),
            )

    def mark_finishing(self, session_id: SessionId, shell_id: ShellId) -> None:
        """Mark all output for one shell as finishing."""
        with self.sqlite_database.write(WorkKind.SOURCES) as connection:
            connection.execute(
                "UPDATE shell_output SET state='finishing' WHERE session_id=? AND shell_id=?",
                (str(session_id), str(shell_id)),
            )

    def outlive_shell(self, session_id: SessionId, shell_id: ShellId) -> None:
        """Move output lifetime from the shell to the session."""
        with self.sqlite_database.write(WorkKind.SOURCES) as connection:
            connection.execute(
                "UPDATE shell_output SET until='session_finished', state='active' WHERE session_id=? AND shell_id=?",
                (str(session_id), str(shell_id)),
            )


class SqliteShellOutputRepository(ShellOutputTransitions, ShellOutputRepository):
    """Store shell output following rows."""

    def __init__(self, sqlite_database: SqliteDatabase) -> None:
        """Initialize the object."""
        self.sqlite_database = sqlite_database

    def save(self, shell_output_following: ShellOutputFollowing) -> None:
        """Save save."""
        with self.sqlite_database.write(WorkKind.SOURCES) as connection:
            connection.execute(
                f"INSERT OR IGNORE INTO shell_output({_COLUMNS}) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                astuple(mapper.shell_output_row(shell_output_following)),
            )

    def oldest_created_at(self) -> float | None:
        """Find the next output that will reach its lifetime limit.

        Returns:
            The oldest start time, or None if no output remains.

        """
        with self.sqlite_database.read() as connection:
            row = connection.execute("SELECT MIN(created_at) AS oldest FROM shell_output").fetchone()
        return None if row["oldest"] is None else float(row["oldest"])

    def find_for_session(self, session_id: SessionId) -> tuple[ShellOutputFollowing, ...]:
        """Return for session.

        Returns:
            For session.

        """
        with self.sqlite_database.read() as connection:
            found = connection.execute(
                "SELECT * FROM shell_output WHERE session_id=? ORDER BY created_at, shell_id, source_path",
                (str(session_id),),
            ).fetchall()
        return tuple(mapper.shell_output_following(rows.shell_output(row)) for row in found)

    def remove(self, session_id: SessionId, shell_id: ShellId, source_path: str) -> None:
        """Remove remove."""
        with self.sqlite_database.write() as connection:
            connection.execute(
                "DELETE FROM shell_output WHERE session_id=? AND shell_id=? AND source_path=?",
                (str(session_id), str(shell_id), source_path),
            )

    def remove_expired(self, created_before: float) -> tuple[ShellOutputFollowing, ...]:
        """Remove expired.

        Returns:
            Result items.

        """
        with self.sqlite_database.write() as connection:
            found = connection.execute(
                "SELECT * FROM shell_output WHERE created_at < ?",
                (created_before,),
            ).fetchall()
            if found:
                connection.execute(
                    "DELETE FROM shell_output WHERE created_at < ?",
                    (created_before,),
                )
        return tuple(mapper.shell_output_following(rows.shell_output(row)) for row in found)
