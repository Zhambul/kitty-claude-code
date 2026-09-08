# Copyright (c) 2026 Zhambyl Yermagambet
"""Read the Claude Code plan dialog from terminal text."""

import re
from dataclasses import dataclass

from domain.ids import WindowId
from harness.impl.claude_code.controls import numberedmenu
from harness.impl.claude_code.controls.plan_models import PlanError
from harness.impl.claude_code.controls.screen_protocols import ScreenDriver

PROCEED_MARKER = "Would you like to proceed?"
FEEDBACK_LABEL = "Tell Claude what to change"
ROW_PATTERN = re.compile(r"^\s*(?P<cursor>\u276f\s+)?(?P<digit>\d+)\.\s+(?P<label>.+?)\s*$")


@dataclass(frozen=True)
class Row:
    """Describe one parsed plan decision row."""

    digit: str
    label: str
    cursor: bool
    feedback: bool


def region(screen: str) -> str:
    """Return the last visible plan decision region.

    Returns:
        The visible plan decision region.

    """
    marker_index = screen.rfind(PROCEED_MARKER)
    return screen[marker_index:] if marker_index >= 0 else ""


def dialog_open(screen: str) -> bool:
    """Return true when the plan decision region is visible.

    Returns:
        True if the plan decision region is visible.

    """
    return bool(region(screen))


def rows(screen: str) -> list[Row]:
    """Parse all numbered rows in the visible plan region.

    Returns:
        The parsed plan rows.

    """
    parsed_rows: list[Row] = []
    for screen_line in region(screen).splitlines():
        row_match = ROW_PATTERN.match(screen_line)
        if row_match is None:
            continue
        label = row_match.group("label").strip()
        parsed_rows.append(
            Row(
                row_match.group("digit"),
                label,
                bool(row_match.group("cursor")),
                label.startswith(FEEDBACK_LABEL),
            ),
        )
    return parsed_rows


def dialog_closed(screen: str) -> bool:
    """Check whether the plan dialog is absent.

    Returns:
        True if the plan decision region is absent.

    """
    return not dialog_open(screen)


def numbered_rows(screen_driver: ScreenDriver, window_id: WindowId) -> tuple[numberedmenu.Row, ...]:
    """Return plan rows in the shared numbered-menu format.

    Returns:
        The plan rows in the shared menu format.

    """
    return tuple(
        numberedmenu.Row(row.digit, row.label, row.cursor)
        for row in open_rows(screen_driver, window_id)
    )


def open_rows(screen_driver: ScreenDriver, window_id: WindowId) -> list[Row]:
    """Return visible plan rows or report an invalid screen.

    Returns:
        The visible plan rows.

    Raises:
        PlanError: If the plan dialog or its rows are not visible.

    """
    screen = screen_driver.read_text(window_id) or ""
    if not dialog_open(screen):
        message = "open"
        raise PlanError(message, "no plan dialog on screen")
    visible_rows = rows(screen)
    if not visible_rows:
        message = "open"
        raise PlanError(message, "plan dialog has no option rows")
    return visible_rows
