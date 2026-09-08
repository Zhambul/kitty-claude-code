# Copyright (c) 2026 Zhambyl Yermagambet
"""Results from pane commands."""

from __future__ import annotations

from dataclasses import dataclass

from terminal.models.values import WindowId


@dataclass(frozen=True)
class PaneOpenResponse:
    """Report the result of a pane open command."""

    succeeded: bool
    window_id: WindowId | None
    reason: str | None = None


@dataclass(frozen=True)
class PaneCloseResponse:
    """Report the result of a pane close command."""

    succeeded: bool
    reason: str | None = None


@dataclass(frozen=True)
class PaneResizeResponse:
    """Report the result of a pane resize command."""

    succeeded: bool
    reason: str | None = None


@dataclass(frozen=True)
class WindowFocusResponse:
    """Report the result of a window focus command."""

    succeeded: bool
    reason: str | None = None
