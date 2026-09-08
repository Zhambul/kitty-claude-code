# Copyright (c) 2026 Zhambyl Yermagambet
"""Map SQLite audit rows to repository row objects."""

from __future__ import annotations

from typing import TYPE_CHECKING

from repository.impl.sqlite.row_columns import ID_COLUMN, SESSION_ID_COLUMN
from repository.model.audit import ErrorRow, SpawnRow, StateFileRow

if TYPE_CHECKING:
    import sqlite3


def error(row: sqlite3.Row) -> ErrorRow:
    """Return the error row.

    Returns:
        The error row.

    """
    return ErrorRow(
        id=row[ID_COLUMN],
        ts=row["ts"],
        session_id=row[SESSION_ID_COLUMN],
        script=row["script"],
        func=row["func"],
        traceback=row["traceback"],
        context=row["context"],
        pid=row["pid"],
    )


def state_file(row: sqlite3.Row) -> StateFileRow:
    """Return the state file row.

    Returns:
        The state file row.

    """
    return StateFileRow(
        id=row[ID_COLUMN],
        ts=row["ts"],
        session_id=row[SESSION_ID_COLUMN],
        path=row["path"],
        action=row["action"],
        content=row["content"],
        script=row["script"],
        pid=row["pid"],
    )


def spawn(row: sqlite3.Row) -> SpawnRow:
    """Return the spawn row.

    Returns:
        The spawn row.

    """
    return SpawnRow(
        id=row[ID_COLUMN],
        ts=row["ts"],
        session_id=row[SESSION_ID_COLUMN],
        parent_script=row["parent_script"],
        child_pid=row["child_pid"],
        argv=row["argv"],
        purpose=row["purpose"],
    )
