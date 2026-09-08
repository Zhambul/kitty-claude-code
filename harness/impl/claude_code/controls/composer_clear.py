# Copyright (c) 2026 Zhambyl Yermagambet
"""Clear and verify the Claude Code composer."""

import time
from collections.abc import Callable

from domain.ids import WindowId
from harness.impl.claude_code import suggestion, suggestion_screen
from harness.impl.claude_code.controls.screen_protocols import ScreenDriver

CLEAR_GAP_SECONDS = 0.15
CLEAR_EFFECT_TIMEOUT_SECONDS = 1.5
CLEAR_LINES_MAXIMUM = 50


def clear_input(
    screen_driver: ScreenDriver,
    window_id: WindowId,
    previous_text: str = "",
    sleep: Callable[[float], None] = time.sleep,
) -> int:
    """Clear a draft and verify each removed logical line.

    Returns:
        The number of removed logical lines.

    """
    before = _input_text(screen_driver, window_id)
    if not before:
        return 0
    for removed_lines in range(1, CLEAR_LINES_MAXIMUM + 1):
        screen_driver.send_key(window_id, "ctrl+u")
        screen_driver.send_key(window_id, "ctrl+k")
        after = _wait_for_input_change(screen_driver, window_id, before, sleep)
        if _input_clear_is_done(
            after,
            before,
            removed_lines,
            _fallback_line_count(previous_text),
        ):
            return removed_lines
        screen_driver.send_key(window_id, "backspace")
        joined = _wait_for_input_change(screen_driver, window_id, after, sleep)
        before = after if joined is None else joined
    return CLEAR_LINES_MAXIMUM


def _fallback_line_count(previous_text: str) -> int:
    return min(
        previous_text.count("\n") + 1 if previous_text else 1,
        CLEAR_LINES_MAXIMUM,
    )


def _input_clear_is_done(
    after: str | None,
    before: str | None,
    removed_lines: int,
    fallback_lines: int,
) -> bool:
    if after is None:
        return removed_lines >= fallback_lines
    return not after or after == before


def _wait_for_input_change(
    screen_driver: ScreenDriver,
    window_id: WindowId,
    before: str | None,
    sleep: Callable[[float], None],
) -> str | None:
    deadline = time.monotonic() + CLEAR_EFFECT_TIMEOUT_SECONDS
    while True:
        current = _input_text(screen_driver, window_id)
        if current != before:
            return current
        if time.monotonic() >= deadline:
            return current
        sleep(CLEAR_GAP_SECONDS)


def _input_text(screen_driver: ScreenDriver, window_id: WindowId) -> str | None:
    for ansi in (True, False):
        screen = screen_driver.read_text(window_id, ansi=ansi)
        if screen is None:
            continue
        if not suggestion_screen.input_box_visible(screen):
            return None
        return suggestion.typed(screen) or ""
    return None
