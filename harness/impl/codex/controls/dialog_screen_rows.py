# Copyright (c) 2026 Zhambyl Yermagambet
"""Read Codex question-dialog option rows."""

import re

from harness.impl.codex.controls.dialog_models import OptionRow, Prompt

NONE_LABEL = "None of the above"
NONE_PREFIX = "None of the"
OPTION = re.compile(r"^\s*(?P<cur>[\u203a\u276f]\s+)?(?P<num>\d+)\.\s+(?P<label>.+?)(?:\s{2,}.*)?\s*$")


def _option_row(row_match: re.Match[str]) -> OptionRow:
    return OptionRow(
        row_match.group("num"),
        row_match.group("label").strip(),
        bool(row_match.group("cur")),
    )


def rows(screen: str) -> list[OptionRow]:
    """Return numbered option rows in display order.

    Returns:
        Numbered option rows in display order.

    """
    option_rows: list[OptionRow] = []
    for screen_line in screen.splitlines():
        row_match = OPTION.match(screen_line)
        if row_match:
            option_rows.append(_option_row(row_match))
    return option_rows


def row_number(screen: str, label: str, prefix: str = "") -> str:
    """Return the option number that has the given label.

    Returns:
        The option number that has the given label.

    """
    option_rows = rows(screen)
    exact = next((row.num for row in option_rows if row.label == label), "")
    if exact or not prefix:
        return exact
    return next((row.num for row in option_rows if row.label.startswith(prefix)), "")


def none_row(screen: str, prompt: Prompt) -> str:
    """Return the free-text option row number.

    Returns:
        The free-text option row number.

    """
    found = row_number(screen, NONE_LABEL, NONE_PREFIX)
    if found:
        return found
    option_rows = rows(screen)
    expected_count = len(prompt.options) + 1
    if not prompt.options or len(option_rows) != expected_count:
        return ""
    last_row = option_rows[-1]
    if last_row.num == str(expected_count):
        return last_row.num
    return ""


def cursor_row(screen: str) -> OptionRow | None:
    """Return the option row that has the cursor.

    Returns:
        The option row that has the cursor.

    """
    return next((row for row in rows(screen) if row.cursor), None)
