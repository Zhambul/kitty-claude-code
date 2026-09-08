# Copyright (c) 2026 Zhambyl Yermagambet
"""SQLite automatic-title job queue."""

from __future__ import annotations

from typing import TYPE_CHECKING

from domain.ids import SessionId
from domain.naming import NamingJob, NamingJobState

if TYPE_CHECKING:
    import sqlite3

    from repository.impl.sqlite.connection import SqliteDatabase


class SqliteNamingJobRepository:
    """Represent sqlite naming job repository."""

    def __init__(self, sqlite_database: SqliteDatabase) -> None:
        """Initialize the object."""
        self.database = sqlite_database

    def enqueue(self, naming_job: NamingJob) -> bool:
        """Return the enqueue.

        Returns:
            Enqueue.

        """
        with self.database.write() as connection:
            cursor = connection.execute(
                "INSERT OR IGNORE INTO naming_jobs(job_key, session_id, prompt, state) VALUES(?, ?, ?, 'pending')",
                (naming_job.key, str(naming_job.session_id), naming_job.prompt),
            )
        return cursor.rowcount == 1

    def register_running(self, naming_job: NamingJob) -> tuple[NamingJob, bool]:
        """Register running.

        Returns:
            Result items.

        Raises:
            RuntimeError: If the operation cannot continue.

        """
        with self.database.write() as connection:
            inserted = connection.execute(
                "INSERT OR IGNORE INTO naming_jobs(job_key, session_id, prompt, state) VALUES(?, ?, ?, 'running')",
                (naming_job.key, str(naming_job.session_id), naming_job.prompt),
            )
            row = connection.execute(
                "SELECT * FROM naming_jobs WHERE job_key=?",
                (naming_job.key,),
            ).fetchone()
        if row is None:
            message = "naming job disappeared after insert"
            raise RuntimeError(message)
        return _job(row), inserted.rowcount == 1

    def claim_next(self) -> NamingJob | None:
        """Return the claim next.

        Returns:
            Claim next.

        """
        with self.database.write() as connection:
            row = connection.execute(
                "SELECT * FROM naming_jobs WHERE state='pending' ORDER BY id LIMIT 1",
            ).fetchone()
            if row is None:
                return None
            connection.execute(
                "UPDATE naming_jobs SET state='running' WHERE job_key=? AND state='pending'",
                (row["job_key"],),
            )
        return _job(row, naming_job_state=NamingJobState.RUNNING)

    def complete(self, key: str, title: str) -> None:
        """Return the complete."""
        with self.database.write() as connection:
            connection.execute(
                "UPDATE naming_jobs SET state='completed', title=?, error=NULL WHERE job_key=?",
                (title, key),
            )

    def fail(self, key: str, reason: str) -> None:
        """Return the fail."""
        with self.database.write() as connection:
            connection.execute(
                "UPDATE naming_jobs SET state='failed', error=? WHERE job_key=?",
                (reason, key),
            )

    def find(self, key: str) -> NamingJob | None:
        """Return find.

        Returns:
            Find.

        """
        with self.database.read() as connection:
            row = connection.execute(
                "SELECT * FROM naming_jobs WHERE job_key=?",
                (key,),
            ).fetchone()
        return None if row is None else _job(row)


def _job(
    row: sqlite3.Row,
    *,
    naming_job_state: NamingJobState | None = None,
) -> NamingJob:
    return NamingJob(
        key=str(row["job_key"]),
        session_id=SessionId(str(row["session_id"])),
        prompt=str(row["prompt"]),
        state=naming_job_state or NamingJobState(str(row["state"])),
        title=None if row["title"] is None else str(row["title"]),
        error=None if row["error"] is None else str(row["error"]),
    )
