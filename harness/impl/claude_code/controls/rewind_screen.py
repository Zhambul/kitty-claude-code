# Copyright (c) 2026 Zhambyl Yermagambet
"""Read Claude Code rewind menus from terminal text."""

import re

from harness.impl.claude_code.controls import numberedmenu
from harness.impl.claude_code.controls.rewind_models import ClaudeCodeRewindMode, ConfirmOption

MENU_HEADER = "Rewind"
MENU_INTRO = "Restore the code and/or conversation to the point before"
MENU_FOOT = "to continue"
CONFIRM_HEADER = "Confirm you want to restore"
CODE_UNCHANGED = "The code will be unchanged."


def menu_region(screen: str) -> str:
    """Return the last visible rewind menu region.

    Returns:
        The visible rewind menu region.

    """
    if not screen:
        return ""
    header_matches = list(
        re.finditer(
            rf"\n[ \t]+{re.escape(MENU_HEADER)}[ \t]*\n",
            f"\n{screen}",
        ),
    )
    if not header_matches:
        return ""
    region_start = max(0, header_matches[-1].start() - 1)
    return screen[region_start:]


def cursor_entry(screen: str) -> str:
    """Return the selected rewind entry.

    Returns:
        The selected rewind entry.

    """
    cursor_matches = re.findall(r"^\s+\u276f\s+(.*)$", menu_region(screen), re.MULTILINE)
    return cursor_matches[-1].strip() if cursor_matches else ""


def menu_open(screen: str) -> bool:
    """Return true when the checkpoint list is visible.

    Returns:
        True if the checkpoint list is visible.

    """
    visible_region = menu_region(screen)
    marker_visible = MENU_INTRO in visible_region or MENU_FOOT in visible_region.lower()
    return (
        bool(visible_region) and marker_visible and bool(cursor_entry(screen)) and CONFIRM_HEADER not in visible_region
    )


def confirm_open(screen: str) -> bool:
    """Return true when the confirmation menu is visible.

    Returns:
        True if the confirmation menu is visible.

    """
    return CONFIRM_HEADER in menu_region(screen)


def confirm_options(screen: str) -> tuple[ConfirmOption, ...]:
    """Return all visible rewind confirmation options.

    Returns:
        The visible confirmation options.

    """
    return tuple(
        ConfirmOption(row.label.lower(), row.digit, row.cursor)
        for row in numberedmenu.rows(menu_region(screen))
    )


def confirm_ready(screen: str, requested_label: str, mode: str) -> bool:
    """Return true when the menu has enough data for a safe choice.

    Returns:
        True if the menu has enough data for a safe choice.

    """
    if not confirm_open(screen):
        return False
    options = confirm_options(screen)
    if any(option.label == requested_label for option in options):
        return True
    code_mode = mode in {ClaudeCodeRewindMode.BOTH, ClaudeCodeRewindMode.CODE}
    return code_mode and bool(options) and CODE_UNCHANGED in menu_region(screen)


def option_digit(screen: str, requested_label: str) -> str | None:
    """Return the digit for one exact confirmation label.

    Returns:
        The option digit, or None if no option matches.

    """
    return next(
        (option.digit for option in confirm_options(screen) if option.label == requested_label),
        None,
    )
