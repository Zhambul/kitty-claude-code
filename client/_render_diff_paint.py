# Copyright (c) 2026 Zhambyl Yermagambet
"""Split terminal mirror rendering."""

from __future__ import annotations

from typing import TYPE_CHECKING

import _render_styles as styles
from _render_diff_parse import _diff_rows
from _render_line_numbers import _number_prefix
from _render_rows import (
    _RowOptions,
    rows,
)

if TYPE_CHECKING:
    from _render_diff_models import (
        _DiffRow,
    )


def _diff_spans(row: _DiffRow, background: styles.Color) -> list[styles.Span]:
    if row.changed is None:
        return [styles.Span(row.text)]
    start, end = row.changed
    changed_background = (
        styles.REMOVED_CHANGED_BACKGROUND if row.kind == styles.REMOVED_DIFF_ROW else styles.ADDED_CHANGED_BACKGROUND
    )
    return [
        styles.Span(row.text[:start]),
        styles.Span(row.text[start:end], background=changed_background),
        styles.Span(row.text[end:], background=background),
    ]


def _diff_content_rows(unified_diff: str, width: int) -> list[str]:
    parsed = _diff_rows(unified_diff)
    number_width = _diff_number_width(parsed)
    painted: list[str] = []
    for row in parsed:
        painted.extend(_paint_diff_row(row, width, number_width))
    return painted


def _paint_diff_row(row: _DiffRow, width: int, number_width: int) -> list[str]:
    if row.kind == "sep":
        return rows(
            [styles.Span("⋮", styles.DIM)],
            width,
            _RowOptions(
                prefix=(styles.Span(" " * (number_width + 2), styles.DIM),),
                mode=styles.VERBATIM_LAYOUT,
            ),
        )
    if row.number is None:
        message = "a diff content row must have a line number"
        raise ValueError(message)
    if row.kind == "context":
        return rows(
            [styles.Span(row.text)],
            width,
            _RowOptions(
                prefix=_number_prefix(row.number, number_width),
                mode=styles.VERBATIM_LAYOUT,
            ),
        )
    background = styles.REMOVED_BACKGROUND if row.kind == styles.REMOVED_DIFF_ROW else styles.ADDED_BACKGROUND
    return rows(
        _diff_spans(row, background),
        width,
        _RowOptions(
            prefix=_number_prefix(row.number, number_width),
            mode=styles.VERBATIM_LAYOUT,
            background=background,
        ),
    )


def _diff_number_width(rows_to_measure: list[_DiffRow]) -> int:
    width = 1
    for row in rows_to_measure:
        if row.number is not None:
            width = max(width, len(str(row.number)))
    return width
