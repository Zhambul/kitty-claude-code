# Copyright (c) 2026 Zhambyl Yermagambet
"""Split terminal mirror rendering."""

from __future__ import annotations

from typing import TYPE_CHECKING

import _render_styles as styles
from _render_diff_paint import _diff_content_rows
from _render_line_numbers import _number_prefix
from _render_rows import (
    _RowOptions,
    rows,
)
from _render_tools import _entry_text

if TYPE_CHECKING:
    from _model import (
        EntryBodyRecord,
        EntryRecord,
    )


def _file_rows(
    entry: EntryRecord,
    view: styles.Links,
    width: int,
    *,
    open_now: bool,
) -> list[str]:
    """One line per file, and its content beneath when the reader expanded it.

    The whole line is the link, not a marker beside it: the target is the file,
    and a two-character affordance on a line this narrow is a worse click than
    the words themselves.

    Returns:
        Result items.

    """
    body = entry.body
    spans = _file_heading(entry, view, open_now=open_now)
    painted = rows(spans, width, _RowOptions(mode=styles.TRUNCATE_LAYOUT))
    if open_now:
        entry_text = _entry_text(body.content)
        painted.extend(_content_rows(entry_text, body.action or "", width))
    return painted


def _file_heading(entry: EntryRecord, view: styles.Links, *, open_now: bool) -> list[styles.Span]:
    body = entry.body
    verb, color = _file_verb(body)
    if body.state == "failed":
        color = styles.FAILURE
    target = view(entry.entry_id) if body.content else None
    spans = _file_identity_spans(body, verb, color, target, open_now=open_now)
    _append_file_counts(spans, body)
    return spans


def _file_verb(body: EntryBodyRecord) -> tuple[str, styles.Color]:
    action = body.action or ""
    default_verb = "Touch", styles.PRIMARY_TEXT
    return styles.FILE_VERBS.get(action, default_verb)


def _file_identity_spans(
    body: EntryBodyRecord,
    verb: str,
    color: styles.Color,
    target: str | None,
    *,
    open_now: bool,
) -> list[styles.Span]:
    marker = " "
    if target:
        marker = "▸"
    if open_now:
        marker = "▾"
    return [
        styles.Span(f"{marker} ", styles.DIM, link=target),
        styles.Span(verb, color, link=target),
        styles.Span("(", dim=True, link=target),
        styles.Span(body.path or "", link=target),
        styles.Span(")", dim=True, link=target),
    ]


def _file_counts(body: EntryBodyRecord) -> list[styles.Span]:
    counts: list[styles.Span] = []
    if body.lines_added:
        counts.append(styles.Span(f"+{int(body.lines_added)}", styles.SUCCESS))
    if body.lines_removed:
        counts.append(styles.Span(f"-{int(body.lines_removed)}", styles.FAILURE))
    return counts


def _append_file_counts(spans: list[styles.Span], body: EntryBodyRecord) -> None:
    for index, span in enumerate(_file_counts(body)):
        separator = styles.TEXT_INDENT if index == 0 else " "
        spans.extend((styles.Span(separator), span))


def _content_rows(content: str, action: str, width: int) -> list[str]:
    """Return the content rows.

    A file's own text, laid out verbatim.

        Verbatim and not wrapped: this is source or a diff, its columns mean
        something, and re-flowing it is how a diff stops being readable. A row wider
        than the pane is cut rather than folded, for the same reason.

    Returns:
        Content rows.

    """
    if action not in {"read", "created"}:
        return _diff_content_rows(content, width)
    lines = content.splitlines()
    number_width = max(1, len(str(len(lines))))
    painted = []
    for number, line in enumerate(lines, 1):
        painted.extend(
            rows(
                [styles.Span(line)],
                width,
                _RowOptions(
                    prefix=_number_prefix(number, number_width),
                    mode=styles.VERBATIM_LAYOUT,
                ),
            ),
        )
    return painted
