# Copyright (c) 2026 Zhambyl Yermagambet
"""Define terminal observation values for E2E journeys."""

from __future__ import annotations

from dataclasses import dataclass

from terminal.models.values import WindowInfo


@dataclass(frozen=True)
class SessionPaneSet:
    """Represent the three windows for one session."""

    host: WindowInfo
    activity: WindowInfo
    scoreboard: WindowInfo

    @property
    def geometry(self) -> PaneGeometry:
        """The current activity pane geometry."""
        return PaneGeometry(
            activity_columns=self.activity.columns,
            total_columns=self.host.columns + self.activity.columns,
        )


@dataclass(frozen=True)
class PaneGeometry:
    """Represent the width of the activity pane."""

    activity_columns: int
    total_columns: int

    @property
    def percent(self) -> int:
        """The activity pane width as a percent."""
        return round(100 * self.activity_columns / self.total_columns)


@dataclass(frozen=True)
class TerminalFocus:
    """Represent the active terminal window."""

    window_id: str
    tab_id: str
    kitty_focused: bool
