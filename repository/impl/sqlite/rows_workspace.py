# Copyright (c) 2026 Zhambyl Yermagambet
"""Map SQLite workspace rows to repository row objects."""

from __future__ import annotations

from typing import TYPE_CHECKING

from repository.impl.sqlite.row_columns import SESSION_ID_COLUMN
from repository.model.workspace import (
    ComposerQueueItemRow,
    DialogAnswerRow,
    DialogAnswerSelectionRow,
    SessionWorkspaceRow,
)

if TYPE_CHECKING:
    import sqlite3


def session_workspace(row: sqlite3.Row) -> SessionWorkspaceRow:
    """Return the session workspace row.

    Returns:
        The session workspace row.

    """
    return SessionWorkspaceRow(
        session_id=row[SESSION_ID_COLUMN],
        composer_text=row["composer_text"],
        composer_origin=row["composer_origin"],
        composer_sequence=row["composer_sequence"],
        queue_origin=row["queue_origin"],
        dialog_attention_id=row["dialog_attention_id"],
        dialog_origin=row["dialog_origin"],
    )


def composer_queue_item(row: sqlite3.Row) -> ComposerQueueItemRow:
    """Return the composer queue item row.

    Returns:
        The composer queue item row.

    """
    return ComposerQueueItemRow(
        session_id=row[SESSION_ID_COLUMN],
        position=row["position"],
        request_id=row["request_id"],
        text=row["text"],
    )


def dialog_answer(row: sqlite3.Row) -> DialogAnswerRow:
    """Return the dialog answer row.

    Returns:
        The dialog answer row.

    """
    return DialogAnswerRow(
        session_id=row[SESSION_ID_COLUMN],
        prompt_index=row["prompt_index"],
        other_text=row["other_text"],
    )


def dialog_answer_selection(row: sqlite3.Row) -> DialogAnswerSelectionRow:
    """Return the dialog answer selection row.

    Returns:
        The dialog answer selection row.

    """
    return DialogAnswerSelectionRow(
        session_id=row[SESSION_ID_COLUMN],
        prompt_index=row["prompt_index"],
        selection_index=row["selection_index"],
        selected_value=row["selected_value"],
    )
