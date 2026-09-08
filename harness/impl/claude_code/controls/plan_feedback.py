# Copyright (c) 2026 Zhambyl Yermagambet
"""Send feedback through the Claude Code plan dialog."""

from collections.abc import Callable

from domain.ids import WindowId
from harness.impl.claude_code.controls import numberedmenu, plan_screen, plan_selection, screen_driver as screen_actions
from harness.impl.claude_code.controls.plan_models import PlanError
from harness.impl.claude_code.controls.screen_protocols import TextScreenDriver

FEEDBACK_STEP = "feedback"


def normalize(text: str) -> str:
    """Return one-line feedback or report empty input.

    Returns:
        The normalized feedback text.

    Raises:
        PlanError: If the feedback has no text.

    """
    normalized_text = " ".join((text or "").split())
    if not normalized_text:
        raise PlanError(FEEDBACK_STEP, "empty feedback")
    return normalized_text


def select_row(
    text_screen_driver: TextScreenDriver,
    window_id: WindowId,
    sleep: Callable[[float], None],
    poll_seconds: float,
) -> None:
    """Select the visible feedback row and keep the dialog open.

    Raises:
        PlanError: If selection fails or closes the dialog.

    """
    feedback_row = plan_selection.feedback_row(text_screen_driver, window_id)
    try:
        numberedmenu.select(
            numberedmenu.SelectionContext(
                text_screen_driver,
                window_id,
                lambda: plan_screen.numbered_rows(text_screen_driver, window_id),
                sleep,
                poll_seconds,
            ),
            feedback_row.digit,
        )
    except numberedmenu.SelectionError as error:
        raise PlanError(FEEDBACK_STEP, str(error)) from error
    if not plan_screen.dialog_open(text_screen_driver.read_text(window_id) or ""):
        raise PlanError(FEEDBACK_STEP, "feedback row closed the plan dialog")


def send_text(
    text_screen_driver: TextScreenDriver,
    window_id: WindowId,
    text: str,
    sleep: Callable[[float], None],
    timeout_seconds: float,
) -> None:
    """Send plan feedback and wait for the dialog to close.

    Raises:
        PlanError: If delivery fails or the dialog stays open.

    """
    if not text_screen_driver.send_text(window_id, text):
        raise PlanError(FEEDBACK_STEP, "text not delivered")
    _, dialog_closed = screen_actions.poll_until(
        text_screen_driver,
        window_id,
        lambda screen: not plan_screen.dialog_open(screen),
        timeout_seconds,
        sleep,
    )
    if not dialog_closed:
        message = "submit"
        raise PlanError(message, "dialog still open after the feedback")
