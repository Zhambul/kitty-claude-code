# Copyright (c) 2026 Zhambyl Yermagambet
"""Pane widths and opened content views over SQLite."""

from __future__ import annotations

from typing import TYPE_CHECKING

from repository.contract.terminal import PaneWidthRepository

if TYPE_CHECKING:
    from repository.impl.sqlite.connection import SqliteDatabase


class SqlitePaneWidthRepository(PaneWidthRepository):
    """Represent sqlite pane width repository."""

    def __init__(self, sqlite_database: SqliteDatabase) -> None:
        """Initialize the object."""
        self.sqlite_database = sqlite_database

    def width_percent(self, working_directory: str) -> int | None:
        """Return the width percent.

        Returns:
            Width percent.

        """
        with self.sqlite_database.read() as connection:
            row = connection.execute(
                "SELECT width_percent FROM pane_widths WHERE working_directory=?",
                (working_directory,),
            ).fetchone()
        return None if row is None else int(row["width_percent"])

    def remember_width(self, working_directory: str, width_percent: int) -> None:
        """Return the remember width."""
        with self.sqlite_database.write() as connection:
            connection.execute(
                "INSERT INTO pane_widths(working_directory, width_percent) VALUES(?, ?) "
                "ON CONFLICT(working_directory) DO UPDATE SET width_percent=excluded.width_percent",
                (working_directory, width_percent),
            )
