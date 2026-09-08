# Copyright (c) 2026 Zhambyl Yermagambet
"""Read stored state for E2E failure reports."""

from __future__ import annotations

import sqlite3
from contextlib import closing
from typing import TYPE_CHECKING, cast

from tests.e2e.testkit import failure_values

if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path

type ProgressRow = tuple[int | None, int | None, int | None]


def progress_marker(directory: Path) -> tuple[int, int, int]:
    """Return counters that change when stored E2E state changes.

    Returns:
        Counters that change when stored E2E state changes.

    """
    database = directory / "main.db"
    if not database.exists():
        return (0, 0, 0)
    try:
        row = _progress_row(database)
    except sqlite3.Error:
        return (0, 0, 0)
    if row is None:
        return (0, 0, 0)
    row_values = tuple(int(column_value or 0) for column_value in row)
    return (
        row_values[0],
        row_values[1],
        row_values[2],
    )


def _progress_row(database: Path) -> ProgressRow | None:
    with closing(sqlite3.connect(f"file:{database}?mode=ro", uri=True, timeout=1)) as connection:
        return cast(
            "ProgressRow | None",
            connection.execute(
                "SELECT (SELECT COUNT(*) FROM sessions), "
                "(SELECT COUNT(*) FROM raw_events), "
                "(SELECT COUNT(*) FROM canonical_events)",
            ).fetchone(),
        )


def database_state(directory: Path) -> str:
    """Return stored databases for an E2E failure report.

    Returns:
        Stored databases for an E2E failure report.

    """
    sections = ["stored state"]
    sections.extend(
        _query_sections(
            directory / "main.db",
            (
                (
                    "sessions",
                    (
                        "SELECT session_id, harness, harness_session_id, terminal_window_id, "
                        "harness_process_id, lifecycle, working_directory FROM sessions "
                        "ORDER BY created_at DESC LIMIT 30"
                    ),
                ),
                (
                    "recent raw events",
                    (
                        "SELECT id, session_id, harness, source_type, source_position, "
                        "terminal_window_id, harness_process_id FROM raw_events "
                        "ORDER BY id DESC LIMIT 40"
                    ),
                ),
                ("pending raw events", "SELECT COUNT(*) AS count FROM pending_raw_events"),
                (
                    "pipeline cursors",
                    (
                        "SELECT (SELECT MAX(cursor) FROM canonical_events) AS translated, "
                        "(SELECT canonical_cursor FROM reaction_progress) AS reacted, "
                        "(SELECT MAX(cursor) FROM session_entries) AS newest_entry"
                    ),
                ),
                (
                    "recent canonical events",
                    (
                        "SELECT cursor, session_id, event_type, actor_id, turn_id, event_id, "
                        "occurred_at, accepted_at, payload FROM canonical_events "
                        "ORDER BY cursor DESC LIMIT 50"
                    ),
                ),
                (
                    "recent interpretation verdicts",
                    (
                        "SELECT raw_event_id, decision, reason, completed_at FROM interpretations "
                        "ORDER BY completed_at DESC LIMIT 50"
                    ),
                ),
                (
                    "recent session data",
                    "SELECT session_id, revision, payload FROM session_data ORDER BY revision DESC LIMIT 30",
                ),
                (
                    "new-session drafts",
                    "SELECT working_directory, text, sequence FROM new_session_drafts ORDER BY sequence DESC LIMIT 30",
                ),
            ),
        ),
    )
    sections.extend(
        _query_sections(
            directory / "audit.db",
            (
                (
                    "recent control and state records",
                    "SELECT id, ts, session_id, action, content, pid FROM state_files ORDER BY id DESC LIMIT 30",
                ),
                (
                    "recent errors",
                    "SELECT id, ts, session_id, script, func, context, pid FROM errors ORDER BY id DESC LIMIT 30",
                ),
                (
                    "recent spawns",
                    "SELECT id, ts, session_id, child_pid, purpose, argv FROM spawns ORDER BY id DESC LIMIT 30",
                ),
            ),
        ),
    )
    return "\n".join(sections)


def _query_sections(
    database: Path,
    queries: Iterable[tuple[str, str]],
) -> list[str]:
    if not database.exists():
        return [f"  {database.name}: missing"]
    result: list[str] = []
    try:
        connection = sqlite3.connect(
            f"file:{database}?mode=ro",
            uri=True,
            timeout=1,
        )
    except sqlite3.Error as error:
        return [f"  {database.name}: open_error={error}"]
    connection.row_factory = sqlite3.Row
    with closing(connection):
        for label, query in queries:
            result.append(_query_result(connection, label, query))
    return result


def _query_result(connection: sqlite3.Connection, label: str, query: str) -> str:
    try:
        rows = [dict(row) for row in connection.execute(query)]
    except sqlite3.Error as error:
        return f"  {label}: query_error={error}"
    return f"  {label}: {failure_values.compact(rows)}"


def stored_window_ids(directory: Path) -> frozenset[str]:
    """Read only terminal windows that this isolated E2E run observed.

    Returns:
        The stored window identifiers, or an empty set if the database cannot be read.

    """
    database = directory / "main.db"
    if not database.exists():
        return frozenset()
    try:
        return _read_stored_window_ids(database)
    except sqlite3.Error:
        return frozenset()


def _read_stored_window_ids(database: Path) -> frozenset[str]:
    with closing(sqlite3.connect(f"file:{database}?mode=ro", uri=True, timeout=1)) as connection:
        rows = connection.execute(
            "SELECT terminal_window_id FROM sessions "
            "WHERE terminal_window_id IS NOT NULL "
            "UNION SELECT terminal_window_id FROM raw_events "
            "WHERE terminal_window_id IS NOT NULL",
        )
        window_ids: set[str] = set()
        for row in rows:
            window_id = row[0]
            if window_id is not None:
                window_ids.add(str(window_id))
        return frozenset(window_ids)
