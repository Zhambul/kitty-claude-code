# Copyright (c) 2026 Zhambyl Yermagambet
"""The record of what the browser attached.

The bytes are on disk because the harness is handed an `@path`. This is what
makes the directory prunable — `remove_expired` returns the rows so the caller
unlinks; a repository does not touch the filesystem.
"""

from __future__ import annotations

from dataclasses import astuple
from typing import TYPE_CHECKING

from repository.contract.uploads import UploadRepository
from repository.impl.sqlite import rows
from repository.mapper import uploads as mapper

if TYPE_CHECKING:
    from domain.uploads import StoredUpload
    from repository.impl.sqlite.connection import SqliteDatabase


class SqliteUploadRepository(UploadRepository):
    """Represent sqlite upload repository."""

    def __init__(self, sqlite_database: SqliteDatabase) -> None:
        """Initialize the object."""
        self.sqlite_database = sqlite_database

    def record(self, stored_upload: StoredUpload) -> None:
        """Record record."""
        with self.sqlite_database.write() as connection:
            connection.execute(
                "INSERT INTO uploads(upload_id, session_id, name, media_type, byte_size, "
                "stored_path, created_at) VALUES(?, ?, ?, ?, ?, ?, ?)",
                astuple(mapper.upload_row(stored_upload)),
            )

    def remove_expired(self, created_before: float) -> tuple[StoredUpload, ...]:
        """Remove expired.

        Returns:
            Result items.

        """
        with self.sqlite_database.write() as connection:
            found = connection.execute(
                "SELECT * FROM uploads WHERE created_at < ?",
                (created_before,),
            ).fetchall()
            if found:
                connection.execute("DELETE FROM uploads WHERE created_at < ?", (created_before,))
        return tuple(mapper.stored_upload(rows.upload(row)) for row in found)
