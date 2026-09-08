# Copyright (c) 2026 Zhambyl Yermagambet
"""Navigate the Codex question dialog."""

from collections.abc import Callable

from domain.ids import WindowId
from harness.contract import ComposerDriver
from harness.impl.codex.controls.dialog_models import CodexAskError
from harness.impl.codex.controls.dialog_screen_rows import cursor_row
from harness.impl.codex.controls.dialog_screen_state import POLL_SECONDS, notes_open, poll, screen_text

NAVIGATION_LIMIT = 24
STEP_TIMEOUT_SECONDS = 2.5


def cursor_to(
    composer_driver: ComposerDriver, window_id: WindowId, target_number: str, sleep: Callable[[float], None],
) -> None:
    """Move the cursor to an option row."""
    _cursor_to_first(composer_driver, window_id, sleep)
    _cursor_to_number(composer_driver, window_id, target_number, sleep)


def _cursor_to_first(composer_driver: ComposerDriver, window_id: WindowId, sleep: Callable[[float], None]) -> None:
    previous_number: str | None = None
    for _ in range(NAVIGATION_LIMIT):
        current = cursor_row(screen_text(composer_driver, window_id))
        if current is not None and current.num == "1":
            return
        current_number = None if current is None else current.num
        if current_number == previous_number:
            return
        previous_number = current_number
        composer_driver.send_key(window_id, "up")
        sleep(POLL_SECONDS)


def _cursor_to_number(
    composer_driver: ComposerDriver,
    window_id: WindowId,
    target_number: str,
    sleep: Callable[[float], None],
) -> None:
    for _ in range(NAVIGATION_LIMIT):
        current = cursor_row(screen_text(composer_driver, window_id))
        if current is not None and current.num == target_number:
            return
        composer_driver.send_key(window_id, "down")
        sleep(POLL_SECONDS)
    msg = "cursor"
    raise CodexAskError(msg, f"cursor never reached option {target_number}")


def add_note(composer_driver: ComposerDriver, window_id: WindowId, text: str, sleep: Callable[[float], None]) -> None:
    """Open the notes input and paste text.

    Raises:
        CodexAskError: If the notes input does not open or the text cannot be delivered.

    """
    composer_driver.send_key(window_id, "tab")
    _, opened = poll(composer_driver, window_id, notes_open, STEP_TIMEOUT_SECONDS, sleep)
    if not opened:
        msg = "notes"
        raise CodexAskError(msg, "notes field never opened")
    if not composer_driver.paste_text(window_id, text):
        msg = "notes"
        raise CodexAskError(msg, "notes not delivered")
