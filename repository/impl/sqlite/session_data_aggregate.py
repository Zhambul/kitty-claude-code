# Copyright (c) 2026 Zhambyl Yermagambet
"""Assemble session data aggregates from SQLite rows."""

from __future__ import annotations

from typing import TYPE_CHECKING

from domain.session_state import SessionData, SessionFacts
from repository.impl.sqlite import rows
from repository.mapper import session_data as mapper

if TYPE_CHECKING:
    import sqlite3
    from collections.abc import Sequence

    from domain.actor_state import ActorFacts
    from domain.entries import SessionEntry

SESSION_ID_COLUMN = "session_id"
REVISION_COLUMN = "revision"


def session_facts(row: sqlite3.Row) -> SessionFacts:
    """Return session facts from one SQLite row.

    Returns:
        Session facts from one SQLite row.

    """
    return mapper.session_facts(rows.session_data(row))


def actor_facts(row: sqlite3.Row) -> ActorFacts:
    """Return actor facts from one SQLite row.

    Returns:
        Actor facts from one SQLite row.

    """
    return mapper.actor_facts(rows.session_data_actor(row))


def entry(row: sqlite3.Row) -> SessionEntry:
    """Return a session entry from one SQLite row.

    Returns:
        A session entry from one SQLite row.

    """
    return mapper.session_entry(rows.session_entry(row))


def _column_value(row: sqlite3.Row | None, column: str) -> float | None:
    return None if row is None else row[column]


def aggregates(
    session_rows: Sequence[sqlite3.Row],
    actor_rows: Sequence[sqlite3.Row],
    entry_cursors: Sequence[sqlite3.Row],
) -> tuple[SessionData, ...]:
    """Return all session aggregates from related row groups.

    Returns:
        All session aggregates from related row groups.

    """
    actors_by_session: dict[str, list[sqlite3.Row]] = {}
    for row in actor_rows:
        actors_by_session.setdefault(row[SESSION_ID_COLUMN], []).append(row)
    newest_by_session = {entry_cursor[SESSION_ID_COLUMN]: entry_cursor for entry_cursor in entry_cursors}
    return tuple(
        aggregate(
            session_row,
            actors_by_session.get(session_row[SESSION_ID_COLUMN], ()),
            _column_value(newest_by_session.get(session_row[SESSION_ID_COLUMN]), "cursor"),
            _column_value(newest_by_session.get(session_row[SESSION_ID_COLUMN]), "occurred_at"),
        )
        for session_row in session_rows
    )


def aggregate(
    session_row: sqlite3.Row,
    actor_rows: Sequence[sqlite3.Row],
    newest_entry_cursor: float | None,
    newest_entry_at: float | None,
) -> SessionData:
    """Return one session aggregate from its related rows.

    Returns:
        One session aggregate from its related rows.

    """
    actors = tuple(actor_facts(row) for row in actor_rows)
    revisions = (
        [int(session_row[REVISION_COLUMN])]
        + [int(row[REVISION_COLUMN]) for row in actor_rows]
        + [int(newest_entry_cursor or 0)]
    )
    return SessionData(
        session=session_facts(session_row),
        actors=actors,
        cursor=max(revisions),
        last_activity_at=newest_entry_at,
    )
