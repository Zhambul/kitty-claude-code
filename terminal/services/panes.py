# Copyright (c) 2026 Zhambyl Yermagambet
"""The activity pane's width: what you remembered, and what is configured.

The repository answers "is there a stored width for this project"; the DEFAULT
is policy and lives here, resolved once instead of at both of the store's exits.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

from terminal.panes.reaction import PaneWidthReader

if TYPE_CHECKING:
    from repository.contract.terminal import PaneWidthRepository

DEFAULT_WIDTH_PERCENT = 25
DEFAULT_RESIZE_COLUMNS = 4
MINIMUM_PANE_WIDTH_PERCENT = 1
MAXIMUM_PANE_WIDTH_PERCENT = 99


def _configured_integer(name: str, default: int) -> int:
    configured = os.environ.get(name)
    return int(configured) if configured else default


def configured_width_percent() -> int:
    """Return the configured width percent.

    Returns:
        Configured width percent.

    Raises:
        ValueError: If an input value is not valid.

    """
    width = _configured_integer("BAQYLAU_ACTIVITY_WIDTH_PERCENT", DEFAULT_WIDTH_PERCENT)
    if not MINIMUM_PANE_WIDTH_PERCENT <= width <= MAXIMUM_PANE_WIDTH_PERCENT:
        message = "activity pane width must be between 1 and 99 percent"
        raise ValueError(message)
    return width


def resize_columns() -> int:
    """Return the resize columns.

    Returns:
        Resize columns.

    Raises:
        ValueError: If an input value is not valid.

    """
    columns = _configured_integer("BAQYLAU_ACTIVITY_RESIZE_COLUMNS", DEFAULT_RESIZE_COLUMNS)
    if columns <= 0:
        message = "activity pane resize step must be positive"
        raise ValueError(message)
    return columns


class PaneWidthService(PaneWidthReader):
    """Represent pane width service."""

    def __init__(self, pane_width_repository: PaneWidthRepository) -> None:
        """Initialize the object."""
        self.widths = pane_width_repository
        self._configured_width_percent = configured_width_percent()
        self._resize_columns = resize_columns()

    def width_percent(self, working_directory: str) -> int:
        """Return the width percent.

        The remembered width for this project, else the configured default.

        Returns:
            Width percent.

        """
        stored = self.widths.width_percent(os.path.realpath(working_directory))
        return self._configured_width_percent if stored is None else stored

    def remember_width(self, working_directory: str, width_percent: int) -> None:
        """Return the remember width.

        Raises:
            ValueError: If an input value is not valid.

        """
        if not MINIMUM_PANE_WIDTH_PERCENT <= width_percent <= MAXIMUM_PANE_WIDTH_PERCENT:
            message = "activity pane width must be between 1 and 99 percent"
            raise ValueError(message)
        self.widths.remember_width(os.path.realpath(working_directory), width_percent)

    def configured_width_percent(self) -> int:
        """Return the configured width percent.

        Returns:
            Configured width percent.

        """
        return self._configured_width_percent

    def resize_columns(self) -> int:
        """Return the resize columns.

        Returns:
            Resize columns.

        """
        return self._resize_columns
