# Copyright (c) 2026 Zhambyl Yermagambet
"""Read the Claude Code question dialog from terminal text."""

import re
from dataclasses import dataclass

from harness.impl.claude_code.canonical.records import Question
from harness.impl.claude_code.controls import ask_question_match

FOOT = "Enter to select"
REVIEW = "Review your answers"
CHAT_LABEL = "Chat about this"
SUBMIT_LABEL = "Submit answers"

NUMBERED_ROW_PATTERN = re.compile(
    r"^\s*(?P<cursor>\u276f\s+)?(?P<digit>\d+)\.\s+"
    r"(?:\[(?P<check>[ ✔x])\]\s*)?"
    r"(?P<label>.+?)"
    r"(?:\s{2,}[─-╿].*)?\s*$",
)
ACTION_ROW_PATTERN = re.compile(
    r"^\s*(?P<cursor>\u276f\s+)?"
    r"(?P<label>Next|Submit|Chat about this)\s*$",
)


@dataclass(frozen=True)
class Row:
    """Describe one cursor-navigable question dialog row."""

    digit: str
    label: str
    cursor: bool
    check: bool | None

    @classmethod
    def action(cls, action_match: re.Match[str]) -> "Row":
        """Build an unnumbered action row.

        Returns:
            The parsed action row.

        """
        action_label = action_match.group("label")
        selected = bool(action_match.group("cursor"))
        return cls("", action_label, selected, None)


def region(screen: str) -> str:
    """Return the visible question dialog region.

    Returns:
        The visible dialog region.

    """
    if not screen:
        return ""
    screen_lines = screen.splitlines()
    region_start: int | None = None
    for line_index, screen_line in enumerate(screen_lines):
        if "☐" in screen_line or "☒" in screen_line:
            region_start = line_index
    if region_start is not None:
        return "\n".join(screen_lines[region_start:])
    if FOOT in screen or REVIEW in screen:
        return screen
    return ""


def dialog_open(screen: str) -> bool:
    """Return true when the question pane is visible.

    Returns:
        True if the question pane is visible.

    """
    return FOOT in region(screen)


def review_open(screen: str) -> bool:
    """Return true when the review pane is visible.

    Returns:
        True if the review pane is visible.

    """
    return REVIEW in region(screen)


def rows(screen: str) -> list[Row]:
    """Return all cursor-navigable rows in screen order.

    Returns:
        The parsed dialog rows.

    """
    parsed_rows: list[Row] = []
    for screen_line in region(screen).splitlines():
        numbered_match = NUMBERED_ROW_PATTERN.match(screen_line)
        if numbered_match is not None:
            parsed_rows.append(
                Row(
                    numbered_match.group("digit"),
                    numbered_match.group("label").strip(),
                    bool(numbered_match.group("cursor")),
                    None if numbered_match.group("check") is None else numbered_match.group("check") != " ",
                ),
            )
            continue
        action_match = ACTION_ROW_PATTERN.match(screen_line)
        if action_match is not None:
            parsed_rows.append(Row.action(action_match))
    return parsed_rows


def current_question(screen: str, questions: list[Question]) -> int | None:
    """Return the question that the dialog shows.

    Returns:
        The visible question index, or None.

    """
    visible_region = region(screen)
    if REVIEW in visible_region:
        return None
    visible_labels = {row.label for row in rows(screen)}
    return ask_question_match.current_question(visible_region, visible_labels, questions)


def cursor_row(screen: str) -> Row | None:
    """Return the first selected dialog row.

    Returns:
        The selected row, or None if no cursor is visible.

    """
    return next((row for row in rows(screen) if row.cursor), None)
