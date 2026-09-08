# Copyright (c) 2026 Zhambyl Yermagambet
"""Map SQLite session rows to repository row objects."""

from __future__ import annotations

from typing import TYPE_CHECKING

from repository.impl.sqlite.row_columns import (
    CREATED_AT_COLUMN,
    HARNESS_COLUMN,
    SESSION_ID_COLUMN,
    WORKING_DIRECTORY_COLUMN,
)
from repository.model.facts import SessionRow

if TYPE_CHECKING:
    import sqlite3


def session(row: sqlite3.Row) -> SessionRow:
    """Return the session row.

    Returns:
        The session row.

    """
    return SessionRow(
        session_id=row[SESSION_ID_COLUMN],
        lead_actor_id=row["lead_actor_id"],
        harness=row[HARNESS_COLUMN],
        source_reference=row["source_reference"],
        working_directory=row[WORKING_DIRECTORY_COLUMN],
        project_directory=row["project_directory"],
        terminal_window_id=row["terminal_window_id"],
        harness_process_id=row["harness_process_id"],
        created_at=row[CREATED_AT_COLUMN],
    )
