# Copyright (c) 2026 Zhambyl Yermagambet
"""Control the native Claude Code plan decision dialog."""

import time
from collections.abc import Callable

from domain.ids import WindowId
from harness.impl.claude_code.controls import (
    numberedmenu,
    plan_feedback,
    plan_screen,
    plan_selection,
    screen_driver as screen_actions,
)
from harness.impl.claude_code.controls.plan_models import Decided, Dismissed, Fedback, Option, PlanError
from harness.impl.claude_code.controls.screen_protocols import ScreenDriver, TextScreenDriver

POLL_SECONDS = 0.15
STEP_TIMEOUT_SECONDS = 2.5
SUBMIT_TIMEOUT_SECONDS = 4.0
DISMISS_ATTEMPTS = 2


def options(screen_driver: ScreenDriver, window_id: WindowId) -> list[Option]:
    """Return the plan options that are visible now.

    Returns:
        The visible plan options.

    """
    return [
        Option(row.digit, row.label, row.feedback)
        for row in plan_screen.open_rows(screen_driver, window_id)
    ]


def decide(
    screen_driver: ScreenDriver,
    window_id: WindowId,
    digit: str,
    label: str,
    sleep: Callable[[float], None] = time.sleep,
) -> Decided:
    """Select a verified plan decision row.

    Returns:
        The completed decision.

    Raises:
        PlanError: If the row cannot be selected or the dialog stays open.

    """
    plan_selection.decision_row(screen_driver, window_id, digit, label)
    try:
        numberedmenu.select(
            numberedmenu.SelectionContext(
                screen_driver,
                window_id,
                lambda: plan_screen.numbered_rows(screen_driver, window_id),
                sleep,
                POLL_SECONDS,
            ),
            str(digit),
        )
    except numberedmenu.SelectionError as error:
        message = "option"
        raise PlanError(message, str(error)) from error
    _, dialog_closed = screen_actions.poll_until(
        screen_driver,
        window_id,
        plan_screen.dialog_closed,
        SUBMIT_TIMEOUT_SECONDS,
        sleep,
    )
    if not dialog_closed:
        message = "submit"
        raise PlanError(message, "dialog still open after the decision")
    return Decided(label)


def feedback(
    text_screen_driver: TextScreenDriver,
    window_id: WindowId,
    text: str,
    sleep: Callable[[float], None] = time.sleep,
) -> Fedback:
    """Reject the plan with text through its feedback row.

    Returns:
        The completed feedback decision.

    """
    normalized_text = plan_feedback.normalize(text)
    plan_feedback.select_row(text_screen_driver, window_id, sleep, POLL_SECONDS)
    plan_feedback.send_text(
        text_screen_driver,
        window_id,
        normalized_text,
        sleep,
        SUBMIT_TIMEOUT_SECONDS,
    )
    return Fedback(feedback=True)


def dismiss(
    screen_driver: ScreenDriver,
    window_id: WindowId,
    sleep: Callable[[float], None] = time.sleep,
) -> Dismissed:
    """Dismiss the plan and keep the harness in plan mode.

    Returns:
        The completed dismissal.

    Raises:
        PlanError: If the dialog stays open.

    """
    for _ in range(DISMISS_ATTEMPTS):
        # A newly drawn dialog can miss the first key. Retry only while the
        # plan options remain visible, and stop as soon as the dialog closes.
        plan_screen.open_rows(screen_driver, window_id)
        if not screen_driver.send_key(window_id, "escape"):
            msg = "submit"
            raise PlanError(msg, "Escape was not delivered")
        screen, dialog_closed = screen_actions.poll_until(
            screen_driver,
            window_id,
            plan_screen.dialog_closed,
            STEP_TIMEOUT_SECONDS,
            sleep,
        )
        if dialog_closed:
            return Dismissed(dismissed=True)
    msg = "submit"
    raise PlanError(msg, "dialog still open after Escape", screen)
