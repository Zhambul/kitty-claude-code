# Copyright (c) 2026 Zhambyl Yermagambet
"""Check terminal focus during E2E journeys."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tests.e2e.testkit.terminal_models import TerminalFocus
from tests.e2e.testkit.terminal_topology import window_by_id

if TYPE_CHECKING:
    from terminal.models.values import WindowId, WindowInfo


def current_focus(windows: tuple[WindowInfo, ...], current_window_id: WindowId | None) -> TerminalFocus:
    """Return the current terminal focus, or fail when it is unknown.

    Returns:
        The current window, tab, and Kitty application focus state.

    Raises:
        AssertionError: If the current window is unknown or absent from the window list.

    """
    if current_window_id is None:
        msg = "the E2E process has no terminal window"
        raise AssertionError(msg)
    window_id = str(current_window_id)
    found = window_by_id(windows, window_id)
    if found is None:
        msg = f"terminal window {window_id!r} is not on screen"
        raise AssertionError(msg)
    return TerminalFocus(window_id, str(found.tab_id), found.tab_is_focused)
