# Copyright (c) 2026 Zhambyl Yermagambet
"""Fixture builders for terminal contract tests."""

from __future__ import annotations

from typing import TYPE_CHECKING

from terminal.models.values import ACTIVITY_PANE_TAG, RGB, TabAppearance

if TYPE_CHECKING:
    from tests.terminal_contract_remote import JsonValue

IDENTIFIER = "id"
ACTIVE_FOREGROUND = RGB.from_hex("c678dd")
ACTIVE_BACKGROUND = RGB.from_hex("1a0620")
INACTIVE_BACKGROUND = RGB.from_hex("4a2b52")
INACTIVE_FOREGROUND = RGB.from_hex("c0c4cc")


def window_tree() -> list[dict[str, JsonValue]]:
    """Build a focused kitty window tree.

    Returns:
        A focused kitty window tree.

    """
    primary: dict[str, JsonValue] = {
        IDENTIFIER: 7,
        "columns": 75,
        "lines": 40,
        "is_active": True,
        "user_vars": {"baqylau_session": "session-one"},
    }
    activity: dict[str, JsonValue] = {
        IDENTIFIER: 8,
        "columns": 25,
        "lines": 35,
        "is_active": False,
        "user_vars": {ACTIVITY_PANE_TAG: "session-one"},
    }
    tab: dict[str, JsonValue] = {IDENTIFIER: 3, "is_active": True, "is_focused": True, "windows": [primary, activity]}
    return [{"is_focused": True, "tabs": [tab]}]


def last_good_tree() -> list[dict[str, JsonValue]]:
    """Build one valid window tree.

    Returns:
        One valid window tree.

    """
    window: dict[str, JsonValue] = {IDENTIFIER: 7, "columns": 75, "lines": 40, "user_vars": {}}
    return [{"tabs": [{IDENTIFIER: 3, "windows": [window]}]}]


def tab_appearance() -> TabAppearance:
    """Build the tab appearance fixture.

    Returns:
        The tab appearance fixture.

    """
    return TabAppearance(ACTIVE_FOREGROUND, ACTIVE_BACKGROUND, INACTIVE_BACKGROUND, INACTIVE_FOREGROUND)
