# Copyright (c) 2026 Zhambyl Yermagambet
"""Value types and small protocols for session terminal operations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from domain.ids import SessionId, WindowId

MINIMUM_PANE_WIDTH_PERCENT = 1
MAXIMUM_PANE_WIDTH_PERCENT = 99
PERCENT_SCALE = 100


class TerminalOutcome(Protocol):
    """Provide the result shared by terminal operations."""

    @property
    def succeeded(self) -> bool:
        """Whether the operation succeeded."""
        ...


def combined_outcomes(outcomes: list[TerminalOutcome], reason: str) -> SessionTerminalResult:
    """Combine terminal operation results.

    Returns:
        Success if every operation succeeded, or failure with the supplied reason.

    """
    succeeded = all(outcome.succeeded for outcome in outcomes)
    return SessionTerminalResult(succeeded, None if succeeded else reason)


class SessionWindow(Protocol):
    """Provide the terminal window last reported by a session."""

    @property
    def terminal_window_id(self) -> WindowId | None:
        """The last reported terminal window."""
        ...


class SessionFinder(Protocol):
    """Find session fields for terminal operations."""

    def find(self, session_id: SessionId) -> SessionWindow | None:
        """Find one session when it exists."""
        ...


@dataclass(frozen=True)
class SessionTerminalResult:
    """Contain one session terminal operation result."""

    succeeded: bool
    reason: str | None = None


@dataclass(frozen=True)
class SessionPaneRequest:
    """Contain the information needed to open session panes."""

    session_id: SessionId
    anchor_window_id: WindowId
    activity_width_percent: int

    def __post_init__(self) -> None:
        """Validate the activity pane width.

        Raises:
            ValueError: If the width is outside the supported percentage range.

        """
        if not MINIMUM_PANE_WIDTH_PERCENT <= self.activity_width_percent <= MAXIMUM_PANE_WIDTH_PERCENT:
            message = "activity pane width must be between 1 and 99 percent"
            raise ValueError(message)
