# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the match module."""
# terminal/impl/kitty/match.py — kitty's match-expression micro-language.
#
# `id:42`, `window_id:42`, `var:name=value` are kitty grammar and are rendered
# HERE and nowhere else. Above this directory a caller states intent — a
# `PaneAnchor`, a window id — and each terminal implementation renders its own
# syntax for it. A second terminal has its own equivalent of this file.

from terminal.models.panes import PaneAnchor
from terminal.models.values import WindowId


def window(window_id: WindowId) -> str:
    """Return the window.

    The WINDOW itself.

    Returns:
        Window.

    """
    return f"id:{window_id}"


def tab_of(window_id: WindowId) -> str:
    """Return the tab of.

    The TAB CONTAINING the window. kitty's tab-scoped commands (close-tab,
        set-tab-title, set-tab-color) match a tab by a window it holds.

    Returns:
        Tab of.

    """
    return f"window_id:{window_id}"


def tagged(tag_name: str, tag_value: str) -> str:
    """Windows carrying a user-var tag.

    Returns:
        Text result.

    """
    return f"var:{tag_name}={tag_value}"


def anchor(pane_anchor: PaneAnchor) -> str:
    """Return the anchor.

    A `PaneAnchor` as the match expression `--next-to` takes.

    Returns:
        Anchor.

    Raises:
        ValueError: If the anchor has no window or tag.

    """
    if pane_anchor.window_id is not None:
        return window(pane_anchor.window_id)
    if pane_anchor.tag is not None:
        tag_name, tag_value = pane_anchor.tag
        return tagged(tag_name, tag_value)
    message = "a pane anchor must name a window or tag"
    raise ValueError(message)
