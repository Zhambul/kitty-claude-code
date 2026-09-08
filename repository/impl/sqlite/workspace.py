# Copyright (c) 2026 Zhambyl Yermagambet
"""A session's unsent work, across four tables.

Every write is one transaction. The draft's sequence guard in particular MUST
be: the daemon serves requests on many threads, each with its own connection, so
a get-then-set would let a second, older write clobber a newer one.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from typing import TYPE_CHECKING

from repository.contract.workspace import SessionWorkspaceRepository
from repository.impl.sqlite import rows
from repository.mapper import workspace as mapper

if TYPE_CHECKING:

    from domain.composer import ComposerDraft, QueuedMessage
    from domain.dialogs import DialogDraft
    from domain.ids import RequestId, SessionId
    from domain.workspace import SessionWorkspace
    from repository.impl.sqlite.connection import SqliteDatabase


def _ensure_workspace(connection: sqlite3.Connection, session_id: SessionId) -> None:
    session_id_text = str(session_id)
    connection.execute(
        "INSERT OR IGNORE INTO session_workspaces(session_id) VALUES(?)",
        (session_id_text,),
    )


@dataclass(frozen=True)
class WorkspaceRows:
    """Hold the rows that form one session workspace."""

    workspace: sqlite3.Row | None
    queue_items: list[sqlite3.Row]
    answers: list[sqlite3.Row]
    selections: list[sqlite3.Row]


def _workspace_rows(
    connection: sqlite3.Connection,
    session_id_text: str,
) -> WorkspaceRows:
    session_parameters = (session_id_text,)
    workspace_row = connection.execute(
        "SELECT * FROM session_workspaces WHERE session_id=?",
        session_parameters,
    ).fetchone()
    queue_items = connection.execute(
        "SELECT * FROM composer_queue_items WHERE session_id=? ORDER BY position",
        session_parameters,
    ).fetchall()
    answers = connection.execute(
        "SELECT * FROM dialog_answers WHERE session_id=? ORDER BY prompt_index",
        session_parameters,
    ).fetchall()
    selections = connection.execute(
        "SELECT * FROM dialog_answer_selections WHERE session_id=? ORDER BY prompt_index, selection_index",
        session_parameters,
    ).fetchall()
    return WorkspaceRows(workspace_row, queue_items, answers, selections)


class SqliteSessionWorkspaceRepository(SessionWorkspaceRepository):
    """Represent sqlite session workspace repository."""

    def __init__(self, sqlite_database: SqliteDatabase) -> None:
        """Initialize the object."""
        self.sqlite_database = sqlite_database

    def find(self, session_id: SessionId) -> SessionWorkspace | None:
        """Return find.

        Returns:
            Find.

        """
        with self.sqlite_database.read() as connection:
            workspace_rows = _workspace_rows(connection, str(session_id))
            if workspace_rows.workspace is None:
                return None
        return mapper.session_workspace(
            rows.session_workspace(workspace_rows.workspace),
            tuple(rows.composer_queue_item(queue_row) for queue_row in workspace_rows.queue_items),
            tuple(rows.dialog_answer(answer) for answer in workspace_rows.answers),
            tuple(rows.dialog_answer_selection(selection) for selection in workspace_rows.selections),
        )

    def save_composer_draft(self, session_id: SessionId, composer_draft: ComposerDraft) -> bool:
        """Save composer draft.

        Returns:
            True when the stated condition is met; otherwise, false.

        """
        session_id_text = str(session_id)
        with self.sqlite_database.write() as connection:
            _ensure_workspace(connection, session_id)
            current = connection.execute(
                "SELECT composer_sequence FROM session_workspaces WHERE session_id=?",
                (session_id_text,),
            ).fetchone()
            if composer_draft.sequence < current["composer_sequence"]:
                return False
            connection.execute(
                "UPDATE session_workspaces SET composer_text=?, composer_origin=?, "
                "composer_sequence=? WHERE session_id=?",
                (
                    composer_draft.text if composer_draft.text.strip() else "",
                    composer_draft.origin,
                    composer_draft.sequence,
                    session_id_text,
                ),
            )
        return True

    def enqueue_composer_message(
        self,
        session_id: SessionId,
        queued_message: QueuedMessage,
        origin: str,
    ) -> None:
        """Return the enqueue composer message."""
        session_id_text = str(session_id)
        with self.sqlite_database.write() as connection:
            _ensure_workspace(connection, session_id)
            connection.execute(
                "UPDATE session_workspaces SET queue_origin=? WHERE session_id=?",
                (origin, session_id_text),
            )
            connection.execute(
                "INSERT OR IGNORE INTO composer_queue_items("
                "session_id, position, request_id, text) "
                "VALUES(?, (SELECT COALESCE(MAX(position), -1) + 1 "
                "FROM composer_queue_items WHERE session_id=?), ?, ?)",
                (
                    session_id_text,
                    session_id_text,
                    str(queued_message.request_id),
                    queued_message.text,
                ),
            )

    def remove_queued_message(self, session_id: SessionId, request_id: RequestId) -> None:
        """Remove queued message."""
        session_id_text = str(session_id)
        with self.sqlite_database.write() as connection:
            connection.execute(
                "DELETE FROM composer_queue_items WHERE session_id=? AND request_id=?",
                (session_id_text, str(request_id)),
            )

    def save_dialog_draft(self, session_id: SessionId, dialog_draft: DialogDraft) -> None:
        """Save dialog draft."""
        session_id_text = str(session_id)
        session_parameters = (session_id_text,)
        with self.sqlite_database.write() as connection:
            _ensure_workspace(connection, session_id)
            connection.execute(
                "UPDATE session_workspaces SET dialog_attention_id=?, dialog_origin=? WHERE session_id=?",
                (str(dialog_draft.attention_id), dialog_draft.origin, session_id_text),
            )
            connection.execute(
                "DELETE FROM dialog_answers WHERE session_id=?",
                session_parameters,
            )
            connection.execute(
                "DELETE FROM dialog_answer_selections WHERE session_id=?",
                session_parameters,
            )
            connection.executemany(
                "INSERT INTO dialog_answers(session_id, prompt_index, other_text) VALUES(?, ?, ?)",
                mapper.dialog_answer_values(session_id, dialog_draft),
            )
            connection.executemany(
                "INSERT INTO dialog_answer_selections("
                "session_id, prompt_index, selection_index, selected_value) VALUES(?, ?, ?, ?)",
                mapper.dialog_selection_values(session_id, dialog_draft),
            )
