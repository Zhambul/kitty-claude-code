# Copyright (c) 2026 Zhambyl Yermagambet
"""Select verified rows from the Claude Code plan screen."""

from domain.ids import WindowId
from harness.impl.claude_code.controls import plan_screen
from harness.impl.claude_code.controls.plan_models import PlanError
from harness.impl.claude_code.controls.screen_protocols import ScreenDriver


def decision_row(
    screen_driver: ScreenDriver,
    window_id: WindowId,
    digit: str,
    label: str,
) -> plan_screen.Row:
    """Return the named decision row when it is still visible.

    Returns:
        The selected decision row.

    Raises:
        PlanError: If the row changed or needs feedback text.

    """
    selected_row = next(
        (row for row in plan_screen.open_rows(screen_driver, window_id) if row.digit == str(digit)),
        None,
    )
    if selected_row is None or selected_row.label != label:
        message = "option"
        raise PlanError(message, f"row {digit} is not {label!r} any more")
    if selected_row.feedback:
        message = "option"
        raise PlanError(message, "the feedback row takes text, not a click")
    return selected_row


def feedback_row(screen_driver: ScreenDriver, window_id: WindowId) -> plan_screen.Row:
    """Return the visible feedback row.

    Returns:
        The visible feedback row.

    Raises:
        PlanError: If no feedback row is visible.

    """
    selected_row = next(
        (row for row in plan_screen.open_rows(screen_driver, window_id) if row.feedback),
        None,
    )
    if selected_row is None:
        message = "feedback"
        raise PlanError(message, "no feedback row on screen")
    return selected_row
