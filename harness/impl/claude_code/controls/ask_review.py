# Copyright (c) 2026 Zhambyl Yermagambet
"""Complete the Claude Code question review pane."""

from harness.impl.claude_code.controls import (
    ask_navigation,
    askdialog_screen as ask_screen,
    screen_driver as screen_actions,
)
from harness.impl.claude_code.controls.ask_models import AskContext, AskError
from harness.impl.claude_code.controls.askdialog_screen import SUBMIT_LABEL

SUBMIT_TIMEOUT_SECONDS = 4.0


def wait_for_review_or_close(ask_context: AskContext) -> str:
    """Wait for the review pane or a closed dialog.

    Returns:
        The final question or review screen.

    Raises:
        AskError: If neither state appears.

    """
    screen, ready = screen_actions.poll_until(
        ask_context.screen_driver,
        ask_context.window_id,
        lambda current_screen: ask_screen.review_open(current_screen) or not ask_screen.dialog_open(current_screen),
        SUBMIT_TIMEOUT_SECONDS,
        ask_context.sleep,
    )
    if not ready:
        message = "review"
        raise AskError(message, "neither the review pane nor submission appeared", screen=screen)
    return screen


def submit(ask_context: AskContext, screen: str) -> None:
    """Submit the review pane when it is open.

    Raises:
        AskError: If the dialog stays open after submission.

    """
    if not ask_screen.review_open(screen):
        return
    ask_navigation.cursor_to(ask_context, lambda row: row.label == SUBMIT_LABEL, "Submit answers")
    ask_context.screen_driver.send_key(ask_context.window_id, "enter")
    _screen, closed = screen_actions.poll_until(
        ask_context.screen_driver,
        ask_context.window_id,
        lambda current_screen: (
            not ask_screen.dialog_open(current_screen) and not ask_screen.review_open(current_screen)
        ),
        SUBMIT_TIMEOUT_SECONDS,
        ask_context.sleep,
    )
    if not closed:
        message = "submit"
        raise AskError(message, "the dialog is still open after Submit answers")
