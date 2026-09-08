# Copyright (c) 2026 Zhambyl Yermagambet
"""Tests for focused live E2E failure reports."""

from __future__ import annotations

import sqlite3
from typing import TYPE_CHECKING

from tests.e2e.testkit.failure_storage import stored_window_ids

if TYPE_CHECKING:
    from pathlib import Path


def test_stored_window_ids_include_only_windows(tmp_path: Path) -> None:
    """Verify stored window identifiers include only windows owned by the end-to-end database."""
    database = tmp_path / "main.db"
    connection = sqlite3.connect(database)
    connection.executescript(
        """
        CREATE TABLE sessions(terminal_window_id TEXT);
        CREATE TABLE raw_events(terminal_window_id TEXT);
        INSERT INTO sessions VALUES ('e2e-host'), (NULL);
        INSERT INTO raw_events VALUES ('e2e-host'), ('e2e-child'), (NULL);
        """,
    )
    connection.close()

    assert stored_window_ids(tmp_path) == frozenset(("e2e-host", "e2e-child"))
