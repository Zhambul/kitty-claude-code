# Copyright (c) 2026 Zhambyl Yermagambet
"""Check screen changes during question dialog navigation."""

from collections.abc import Callable

from harness.impl.claude_code.controls import askdialog_screen as ask_screen, screen_driver as screen_actions
from harness.impl.claude_code.controls.ask_models import NavigationContext
from harness.impl.claude_code.controls.askdialog_screen import Row

KEY_EFFECT_TIMEOUT_SECONDS = 5.0


def screen_changed(previous_screen: str) -> Callable[[str], bool]:
    """Build a predicate for a changed screen.

    Returns:
        A predicate that detects a screen change.

    """
    return lambda current_screen: current_screen != previous_screen


def screen_changed_or_has_cursor(previous_screen: str) -> Callable[[str], bool]:
    """Build a predicate for a changed screen or visible cursor.

    Returns:
        A predicate that detects progress.

    """
    return lambda current_screen: current_screen != previous_screen or ask_screen.cursor_row(current_screen) is not None


def move_up(navigation_context: NavigationContext, previous_screen: str) -> bool:
    """Send an up key and report a visible screen change.

    Returns:
        True if the screen changed.

    """
    navigation_context.screen_driver.send_key(navigation_context.window_id, "up")
    _screen, changed = screen_actions.poll_until(
        navigation_context.screen_driver,
        navigation_context.window_id,
        screen_changed(previous_screen),
        KEY_EFFECT_TIMEOUT_SECONDS,
        navigation_context.sleep,
    )
    return changed


def matching_cursor(screen: str, predicate: Callable[[Row], bool]) -> bool:
    """Return true when a selected row matches a predicate.

    Returns:
        True if a selected row matches.

    """
    return any(
        row.cursor and predicate(row)
        for row in ask_screen.rows(screen)
    )


def visible_row_states(screen: str) -> list[Row]:
    """Return the visible row states.

    Returns:
        The visible row states.

    """
    return ask_screen.rows(screen)


def cursor_identity(navigation_context: NavigationContext) -> tuple[str, str] | None:
    """Return the visible cursor row identity.

    Returns:
        The row digit and label, or None if no cursor is visible.

    """
    screen = navigation_context.screen_driver.read_text(navigation_context.window_id) or ""
    selected_row = ask_screen.cursor_row(screen)
    if selected_row is None:
        return None
    return selected_row.digit, selected_row.label
