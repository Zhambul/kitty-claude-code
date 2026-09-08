# Copyright (c) 2026 Zhambyl Yermagambet
"""Move through Claude Code question dialog rows."""

from collections.abc import Callable

from harness.impl.claude_code.controls import ask_poll, askdialog_screen as ask_screen, screen_driver as screen_actions
from harness.impl.claude_code.controls.ask_models import AskError, NavigationContext
from harness.impl.claude_code.controls.askdialog_screen import Row

NAVIGATION_LIMIT = 24


def reveal_cursor(navigation_context: NavigationContext) -> None:
    """Move a hidden cursor into the terminal viewport.

    Raises:
        AskError: If a key has no visible effect.

    """
    for _ in range(NAVIGATION_LIMIT):
        previous_screen = navigation_context.screen_driver.read_text(navigation_context.window_id) or ""
        if ask_screen.cursor_row(previous_screen) is not None:
            return
        navigation_context.screen_driver.send_key(navigation_context.window_id, "down")
        screen, changed = screen_actions.poll_until(
            navigation_context.screen_driver,
            navigation_context.window_id,
            ask_poll.screen_changed_or_has_cursor(previous_screen),
            ask_poll.KEY_EFFECT_TIMEOUT_SECONDS,
            navigation_context.sleep,
        )
        if not changed:
            message = "cursor"
            raise AskError(message, "down key had no visible effect while it revealed the cursor", screen=screen)


def normalize_cursor(navigation_context: NavigationContext) -> None:
    """Move the visible cursor to the first row when possible."""
    previous_row: tuple[str, str] | None = None
    for _ in range(NAVIGATION_LIMIT):
        current_row = ask_poll.cursor_identity(navigation_context)
        if current_row is not None and current_row[0] == "1":
            return
        if current_row == previous_row:
            return
        previous_row = current_row
        previous_screen = navigation_context.screen_driver.read_text(navigation_context.window_id) or ""
        if not ask_poll.move_up(navigation_context, previous_screen):
            return


def walk_to(navigation_context: NavigationContext, predicate: Callable[[Row], bool], target_description: str) -> str:
    """Walk down to one matching row.

    Returns:
        The screen that contains the selected row.

    Raises:
        AskError: If navigation stops or no row matches.

    """
    screen = ""
    for _ in range(NAVIGATION_LIMIT):
        screen = navigation_context.screen_driver.read_text(navigation_context.window_id) or ""
        if ask_poll.matching_cursor(screen, predicate):
            return screen
        navigation_context.screen_driver.send_key(navigation_context.window_id, "down")
        screen, changed = screen_actions.poll_until(
            navigation_context.screen_driver,
            navigation_context.window_id,
            ask_poll.screen_changed(screen),
            ask_poll.KEY_EFFECT_TIMEOUT_SECONDS,
            navigation_context.sleep,
        )
        if not changed:
            message = "cursor"
            detail = f"down key had no visible effect while it selected {target_description}"
            raise AskError(message, detail, screen=screen)
    visible_rows = ask_poll.visible_row_states(screen)
    message = "cursor"
    detail = f"cursor never reached {target_description}; visible rows: {visible_rows!r}"
    raise AskError(message, detail, screen=screen)


def cursor_to(navigation_context: NavigationContext, predicate: Callable[[Row], bool], target_description: str) -> str:
    """Move the cursor to one matching dialog row.

    Returns:
        The screen that contains the selected row.

    """
    reveal_cursor(navigation_context)
    normalize_cursor(navigation_context)
    return walk_to(navigation_context, predicate, target_description)


def digit_matches(digit: str) -> Callable[[Row], bool]:
    """Build a predicate for one row digit.

    Returns:
        A predicate that matches the digit.

    """
    return lambda row: row.digit == digit
