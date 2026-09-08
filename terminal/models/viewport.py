# Copyright (c) 2026 Zhambyl Yermagambet
"""Viewport operations — reading and scrolling what a window shows."""

from __future__ import annotations

from dataclasses import dataclass

from terminal.models.values import WindowId


@dataclass(frozen=True)
class ScreenReadRequest:
    """Represent screen read request.

    Read the window's VISIBLE viewport — the scrolled-to rows, not the live
        screen's bottom, which is what lets the mirror restore an exact scroll
        position across a reflow. `ansi=True` keeps the SGR formatting escapes (the
        ghost-suggestion probe detects the faint input line by them).
    """

    window_id: WindowId
    ansi: bool = False


@dataclass(frozen=True)
class ScreenReadResponse:
    """Represent screen read response."""

    succeeded: bool
    text: str | None
    reason: str | None = None
