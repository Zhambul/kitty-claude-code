# Copyright (c) 2026 Zhambyl Yermagambet
"""Select option and text rows in a Claude Code question dialog."""

from harness.impl.claude_code.controls import (
    ask_navigation,
    askdialog_screen as ask_screen,
    screen_driver as screen_actions,
)
from harness.impl.claude_code.controls.ask_models import AskContext, AskError
from harness.impl.claude_code.controls.askdialog_screen import Row

POLL_SECONDS = 0.15
STEP_TIMEOUT_SECONDS = 2.5
KEY_GAP_SECONDS = 0.12
LABEL_PREVIEW_LENGTH = 24


def require_text_row(ask_context: AskContext, text_row_digit: str) -> None:
    """Verify that the current dialog has a free-text row.

    Raises:
        AskError: If the free-text row is not visible.

    """
    screen = ask_context.screen_driver.read_text(ask_context.window_id) or ""
    if not any(row.digit == text_row_digit for row in ask_screen.rows(screen)):
        message = "type"
        raise AskError(message, "the preview dialog has no text-answer row; use Chat about this")


def find_option_row(visible_rows: list[Row], option_digit: str, screen: str) -> Row:
    """Return one visible option row.

    Returns:
        The requested option row.

    Raises:
        AskError: If the option row is not visible.

    """
    option_row = next((row for row in visible_rows if row.digit == option_digit), None)
    if option_row is not None:
        return option_row
    visible_options = [(row.digit, row.label, row.check) for row in visible_rows]
    failure_context = f"missing row {option_digit!r}; visible rows {visible_options!r}"
    message = "options"
    raise AskError(message, failure_context, screen=screen)


def toggle_options(ask_context: AskContext, labels: list[str], selected_labels: list[str]) -> None:
    """Make each visible checkbox match the requested state."""
    for option_index, label in enumerate(labels):
        option_digit = str(option_index + 1)
        screen = ask_navigation.cursor_to(
            ask_context,
            ask_navigation.digit_matches(option_digit),
            f"option {option_digit}",
        )
        option_row = find_option_row(ask_screen.rows(screen), option_digit, screen)
        if bool(option_row.check) != (label in selected_labels):
            ask_context.screen_driver.send_key(ask_context.window_id, "enter")
            ask_context.sleep(KEY_GAP_SECONDS)


def enter_other(ask_context: AskContext, other_text: str, text_row_digit: str, *, verify_check: bool) -> None:
    """Enter a free-text answer and optionally verify its checkbox.

    Raises:
        AskError: If delivery or checkbox selection fails.

    """
    require_text_row(ask_context, text_row_digit)
    ask_navigation.cursor_to(ask_context, ask_navigation.digit_matches(text_row_digit), "Type row")
    if not ask_context.screen_driver.paste_text(ask_context.window_id, other_text):
        message = "type"
        raise AskError(message, "other text was not delivered")
    if not verify_check:
        return
    ask_context.sleep(POLL_SECONDS)
    label_prefix = other_text[:LABEL_PREVIEW_LENGTH]
    checked = any(
        row.check
        for row in ask_screen.rows(ask_context.screen_driver.read_text(ask_context.window_id) or "")
        if row.label.startswith(label_prefix)
    )
    if not checked:
        ask_context.screen_driver.send_key(ask_context.window_id, "enter")
    _screen, checked = screen_actions.poll_until(
        ask_context.screen_driver,
        ask_context.window_id,
        lambda current_screen: any(
            row.check for row in ask_screen.rows(current_screen) if row.label.startswith(label_prefix)
        ),
        STEP_TIMEOUT_SECONDS,
        ask_context.sleep,
    )
    if not checked:
        message = "type"
        raise AskError(message, "the custom option was not checked")
