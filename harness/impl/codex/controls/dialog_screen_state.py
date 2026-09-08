# Copyright (c) 2026 Zhambyl Yermagambet
"""Read Codex question-dialog screen state."""

import re
import time
from collections.abc import Callable

from domain.ids import WindowId
from harness.contract import ComposerDriver

Driver = ComposerDriver
POLL_SECONDS = 0.15
FOOT = "to submit"
NOTES_FOOT = "to clear notes"
CONFIRM_HEAD = "Submit with unanswered questions?"
HEADER = re.compile(r"Question\s+(\d+)\s*/\s*(\d+)")


def screen_text(driver: Driver, window_id: WindowId) -> str:
    """Read screen text, or return empty text.

    Returns:
        The visible screen text, or empty text if the driver returns no text.

    """
    return driver.read_text(window_id) or ""


def poll(
    driver: Driver,
    window_id: WindowId,
    predicate: Callable[[str], bool],
    timeout: float,
    sleep: Callable[[float], None],
) -> tuple[str, bool]:
    """Poll the screen until the predicate holds or time ends.

    Returns:
        The last screen text and whether the predicate was satisfied.

    """
    deadline = time.monotonic() + timeout
    screen = screen_text(driver, window_id)
    while not predicate(screen):
        if time.monotonic() >= deadline:
            return screen, False
        sleep(POLL_SECONDS)
        screen = screen_text(driver, window_id)
    return screen, True


def dialog_open(screen: str) -> bool:
    """Return true when the question dialog is visible.

    Returns:
        True when the question dialog is visible.

    """
    return FOOT in screen or NOTES_FOOT in screen


def notes_open(screen: str) -> bool:
    """Return true when the notes input is visible.

    Returns:
        True when the notes input is visible.

    """
    return NOTES_FOOT in screen


def confirm_open(screen: str) -> bool:
    """Return true when unanswered-question confirmation is visible.

    Returns:
        True when unanswered-question confirmation is visible.

    """
    return CONFIRM_HEAD in screen


def current_question(screen: str) -> tuple[int, int] | None:
    """Return the visible question number and count.

    Returns:
        The visible question number and count.

    """
    header_match = HEADER.search(screen)
    if header_match is None:
        return None
    return int(header_match.group(1)), int(header_match.group(2))


def confirmation_closed(screen: str) -> bool:
    """Return true when confirmation is not visible.

    Returns:
        True when confirmation is not visible.

    """
    return not confirm_open(screen)
