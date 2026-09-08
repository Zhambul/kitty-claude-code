# Copyright (c) 2026 Zhambyl Yermagambet
"""Map SQLite preference rows to repository row objects."""

from __future__ import annotations

from typing import TYPE_CHECKING

from repository.impl.sqlite.row_columns import (
    CREATED_AT_COLUMN,
    HARNESS_COLUMN,
    ID_COLUMN,
    SESSION_ID_COLUMN,
    WORKING_DIRECTORY_COLUMN,
)
from repository.model.preferences import (
    HiddenDirectoryRow,
    NewSessionDraftRow,
    NewSessionPreferenceRow,
    PushSigningKeyRow,
    PushSubscriptionRow,
    SessionViewModeRow,
)

if TYPE_CHECKING:
    import sqlite3


def session_view_mode(row: sqlite3.Row) -> SessionViewModeRow:
    """Return the session view mode row.

    Returns:
        The session view mode row.

    """
    return SessionViewModeRow(session_id=row[SESSION_ID_COLUMN], view_mode=row["view_mode"])


def hidden_directory(row: sqlite3.Row) -> HiddenDirectoryRow:
    """Return the hidden directory row.

    Returns:
        The hidden directory row.

    """
    return HiddenDirectoryRow(working_directory=row[WORKING_DIRECTORY_COLUMN], hidden_at=row["hidden_at"])


def new_session_preference(row: sqlite3.Row) -> NewSessionPreferenceRow:
    """Return the new session preference row.

    Returns:
        The new session preference row.

    """
    return NewSessionPreferenceRow(
        id=row[ID_COLUMN],
        working_directory=row[WORKING_DIRECTORY_COLUMN],
        harness=row[HARNESS_COLUMN],
        model=row["model"],
        effort=row["effort"],
    )


def new_session_draft(row: sqlite3.Row) -> NewSessionDraftRow:
    """Return the new session draft row.

    Returns:
        The new session draft row.

    """
    return NewSessionDraftRow(
        working_directory=row[WORKING_DIRECTORY_COLUMN],
        text=row["text"],
        sequence=row["sequence"],
    )


def push_subscription(row: sqlite3.Row) -> PushSubscriptionRow:
    """Return the push subscription row.

    Returns:
        The push subscription row.

    """
    return PushSubscriptionRow(
        endpoint=row["endpoint"],
        public_key=row["public_key"],
        authentication_secret=row["authentication_secret"],
        device_id=row["device_id"],
        device_label=row["device_label"],
        created_at=row[CREATED_AT_COLUMN],
    )


def push_signing_key(row: sqlite3.Row) -> PushSigningKeyRow:
    """Return the push signing key row.

    Returns:
        The push signing key row.

    """
    return PushSigningKeyRow(
        id=row[ID_COLUMN],
        private_key_pem=row["private_key_pem"],
        public_key=row["public_key"],
    )
