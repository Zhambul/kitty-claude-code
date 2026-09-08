# Copyright (c) 2026 Zhambyl Yermagambet
"""Navigate Claude Code rewind menu rows."""

from typing import Never

from harness.impl.claude_code.controls import numberedmenu
from harness.impl.claude_code.controls.rewind_models import MenuError, RewindContext
from harness.impl.claude_code.controls.rewind_screen import (
    confirm_open,
    confirm_ready,
    cursor_entry,
    menu_open,
    menu_region,
)
from harness.impl.claude_code.controls.rewind_text import entry_matches, first_line

POLL_SECONDS = 0.15
SCAN_LIMIT = 100
CONFIRM_SCAN_LIMIT = 10


def scan_confirm(
    rewind_context: RewindContext,
    requested_label: str,
    mode: str,
    key: str,
) -> tuple[str, bool]:
    """Reveal a confirmation option outside the current viewport.

    Returns:
        The screen text and the match state.

    """
    screen = rewind_context.screen_driver.read_text(rewind_context.window_id) or ""
    remaining_attempts = CONFIRM_SCAN_LIMIT + 1
    while remaining_attempts:
        if confirm_ready(screen, requested_label, mode):
            return screen, True
        if not confirm_open(screen):
            return screen, False
        rewind_context.screen_driver.send_key(rewind_context.window_id, key)
        rewind_context.sleep(POLL_SECONDS)
        screen = rewind_context.screen_driver.read_text(rewind_context.window_id) or ""
        remaining_attempts -= 1
    return screen, False


def select_confirm(rewind_context: RewindContext, digit: str) -> None:
    """Select one verified confirmation row.

    Raises:
        MenuError: If the row cannot be selected.

    """
    try:
        numberedmenu.select(
            numberedmenu.SelectionContext(
                rewind_context.screen_driver,
                rewind_context.window_id,
                lambda: numberedmenu.rows(
                    menu_region(rewind_context.screen_driver.read_text(rewind_context.window_id) or ""),
                ),
                rewind_context.sleep,
                POLL_SECONDS,
            ),
            digit,
        )
    except numberedmenu.SelectionError as error:
        message = "select"
        raise MenuError(message, str(error)) from error


def bail(rewind_context: RewindContext) -> None:
    """Close each open rewind menu level."""
    remaining_levels = 2
    while remaining_levels:
        screen = rewind_context.screen_driver.read_text(rewind_context.window_id) or ""
        if not menu_region(screen):
            return
        rewind_context.screen_driver.send_key(rewind_context.window_id, "escape")
        rewind_context.sleep(POLL_SECONDS)
        remaining_levels -= 1


def scan(rewind_context: RewindContext, target: str, key: str) -> tuple[bool, int]:
    """Scan checkpoint rows until one row matches the target prompt.

    Returns:
        The match state and the number of navigation steps.

    """
    steps = 0
    while steps <= SCAN_LIMIT:
        screen = rewind_context.screen_driver.read_text(rewind_context.window_id) or ""
        selected_entry = cursor_entry(screen)
        if entry_matches(selected_entry, target):
            return True, steps
        if not menu_open(screen):
            return False, steps
        rewind_context.screen_driver.send_key(rewind_context.window_id, key)
        steps += 1
        rewind_context.sleep(POLL_SECONDS)
        next_screen = rewind_context.screen_driver.read_text(rewind_context.window_id) or ""
        if cursor_entry(next_screen) == selected_entry:
            return False, steps
    return False, steps


def apply_hint(rewind_context: RewindContext, hint_steps: int, key_gap_seconds: float) -> None:
    """Move by the bounded checkpoint hint without trusting its target."""
    remaining_steps = max(0, min(hint_steps, SCAN_LIMIT))
    while remaining_steps:
        rewind_context.screen_driver.send_key(rewind_context.window_id, "up")
        rewind_context.sleep(key_gap_seconds)
        remaining_steps -= 1
    rewind_context.sleep(POLL_SECONDS)


def scan_both(rewind_context: RewindContext, target: str) -> tuple[bool, int]:
    """Scan up and then down for one checkpoint.

    Returns:
        The match state and the total number of navigation steps.

    """
    matched, upward_steps = scan(rewind_context, target, "up")
    if matched:
        return True, upward_steps
    matched, downward_steps = scan(rewind_context, target, "down")
    return matched, upward_steps + downward_steps


def raise_missing(rewind_context: RewindContext, target: str, preview_length: int) -> Never:
    """Close the menu and report a missing checkpoint.

    Raises:
        MenuError: Always, because the checkpoint is missing.

    """
    failure_screen = rewind_context.screen_driver.read_text(rewind_context.window_id) or ""
    bail(rewind_context)
    message = "find"
    target_preview = first_line(target)[:preview_length]
    raise MenuError(message, f"checkpoint not found: {target_preview!r}", failure_screen)
