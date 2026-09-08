# Copyright (c) 2026 Zhambyl Yermagambet
"""Build terminal model values for tests."""

from collections.abc import Mapping
from typing import TypedDict, Unpack

from terminal.models import values as terminal_values

DEFAULT_WINDOW_COLUMNS = 80


class WindowArguments(TypedDict, total=False):
    """Contain optional fake window fields."""

    tab_id: str
    tags: Mapping[str, str] | None
    columns: int
    lines: int
    is_first_in_tab: bool
    tab_is_active: bool
    tab_is_focused: bool
    is_active_in_tab: bool


def window(
    window_id: str | int,
    **arguments: Unpack[WindowArguments],
) -> terminal_values.WindowInfo:
    """Build one fake terminal window.

    Returns:
        One fake terminal window.

    """
    return terminal_values.WindowInfo(
        window_id=terminal_values.WindowId(str(window_id)),
        tab_id=terminal_values.TabId(arguments.get("tab_id", "tab-one")),
        tags=dict(arguments.get("tags") or {}),
        columns=arguments.get("columns", DEFAULT_WINDOW_COLUMNS),
        lines=arguments.get("lines", 24),
        is_first_in_tab=arguments.get("is_first_in_tab", True),
        tab_is_active=arguments.get("tab_is_active", True),
        tab_is_focused=arguments.get("tab_is_focused", True),
        is_active_in_tab=arguments.get("is_active_in_tab", True),
    )
