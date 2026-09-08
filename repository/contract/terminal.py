# Copyright (c) 2026 Zhambyl Yermagambet
"""Terminal-side state that outlives a window."""

from __future__ import annotations

from typing import Protocol


class PaneWidthRepository(Protocol):
    """Represent pane width repository."""

    def width_percent(self, working_directory: str) -> int | None:
        """Return the width percent.

        The remembered width, or None when this project has none.

                None rather than the configured default: the default is a policy the
                service owns, and resolving it here meant resolving it twice.
        """
        ...

    def remember_width(self, working_directory: str, width_percent: int) -> None:
        """Return the remember width."""
        ...
