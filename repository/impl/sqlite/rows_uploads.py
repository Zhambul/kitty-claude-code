# Copyright (c) 2026 Zhambyl Yermagambet
"""Map SQLite upload rows to repository row objects."""

from __future__ import annotations

from typing import TYPE_CHECKING

from repository.impl.sqlite.row_columns import CREATED_AT_COLUMN, SESSION_ID_COLUMN
from repository.model.uploads import UploadRow

if TYPE_CHECKING:
    import sqlite3


def upload(row: sqlite3.Row) -> UploadRow:
    """Return the upload row.

    Returns:
        The upload row.

    """
    return UploadRow(
        upload_id=row["upload_id"],
        session_id=row[SESSION_ID_COLUMN],
        name=row["name"],
        media_type=row["media_type"],
        byte_size=row["byte_size"],
        stored_path=row["stored_path"],
        created_at=row[CREATED_AT_COLUMN],
    )
