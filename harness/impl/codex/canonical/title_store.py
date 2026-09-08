# Copyright (c) 2026 Zhambyl Yermagambet
"""Read and write rows in the native Codex title index."""

from __future__ import annotations

import sqlite3
from contextlib import closing

from domain.work_state import TitleOrigin
from harness.impl.codex.canonical.title_values import CodexNativeTitle, ThreadTitleFields
from harness.models.controls import TitleWriteOutcome

CONNECT_TIMEOUT_SECONDS = 2.0
LEGACY_TITLE_COLUMN = "title"
UPDATE_NAME = "UPDATE threads SET name=? WHERE id=?"
UPDATE_LEGACY = "UPDATE threads SET title=? WHERE id=?"
SELECT_CURRENT = "SELECT name, title FROM threads WHERE id=?"
SELECT_LEGACY = "SELECT title FROM threads WHERE id=?"


def set_title(database: str, thread_uuid: str, title: str) -> TitleWriteOutcome:
    """Write one native thread title.

    Returns:
        The native title write outcome.

    """
    try:
        with closing(sqlite3.connect(database, timeout=CONNECT_TIMEOUT_SECONDS)) as connection:
            statement = UPDATE_NAME if has_thread_name(connection) else UPDATE_LEGACY
            cursor = connection.execute(statement, (title, thread_uuid))
            connection.commit()
    except sqlite3.Error:
        return TitleWriteOutcome.UNAVAILABLE
    return TitleWriteOutcome.RENAMED if cursor.rowcount else TitleWriteOutcome.UNAVAILABLE


def read_title(database: str, thread_uuid: str) -> CodexNativeTitle | None:
    """Read one native thread title.

    Returns:
        The native title, or ``None`` when it is unavailable.

    """
    fields = thread_title_row(database, thread_uuid)
    if fields is None:
        return None
    title = fields.name or fields.automatic
    return CodexNativeTitle(title, TitleOrigin.AUTOMATIC) if title else None


def thread_title_row(database: str, thread_uuid: str) -> ThreadTitleFields | None:
    """Read the manual and automatic title fields of one native thread.

    Returns:
        The title fields, or ``None`` when the row cannot be read.

    """
    try:
        with closing(sqlite3.connect(database, timeout=CONNECT_TIMEOUT_SECONDS)) as connection:
            connection.row_factory = sqlite3.Row
            current_schema = has_thread_name(connection)
            statement = SELECT_CURRENT if current_schema else SELECT_LEGACY
            row = connection.execute(statement, (thread_uuid,)).fetchone()
    except sqlite3.Error:
        return None
    if row is None:
        return None
    if current_schema:
        return ThreadTitleFields(row_text(row, "name"), row_text(row, LEGACY_TITLE_COLUMN))
    return ThreadTitleFields("", row_text(row, LEGACY_TITLE_COLUMN))


def row_text(row: sqlite3.Row, column: str) -> str:
    """Return a trimmed native title field.

    Returns:
        The field text.

    """
    column_content = row[column]
    return "" if column_content is None else str(column_content).strip()


def has_thread_name(connection: sqlite3.Connection) -> bool:
    """Return whether the native index has a current ``name`` column.

    Returns:
        ``True`` for the current schema.

    """
    return any(
        str(column[1]) == "name"
        for column in connection.execute("PRAGMA table_info(threads)")
    )
