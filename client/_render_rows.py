# Copyright (c) 2026 Zhambyl Yermagambet
"""Split terminal mirror rendering."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from _render_span_operations import _painted, _take
from _render_styles import (
    TRUNCATE_LAYOUT,
    VERBATIM_LAYOUT,
    Color,
    Span,
)
from _render_wrap import (
    _split_lines,
    _WrapState,
)

if TYPE_CHECKING:
    from collections.abc import Iterable


def _no_link(_subject_name: str) -> str:
    return ""


@dataclass(frozen=True)
class _RowOptions:
    prefix: tuple[Span, ...] = ()
    continuation: tuple[Span, ...] | None = None
    mode: str = "word_wrap"
    background: Color | None = None


DEFAULT_ROW_OPTIONS = _RowOptions()


def rows(
    spans: Iterable[Span],
    width: int,
    options: _RowOptions = DEFAULT_ROW_OPTIONS,
) -> list[str]:
    r"""One logical line as the screen rows it occupies.

    Three layouts, and each exists for something the pane draws: `word_wrap` for
    prose and command output, `truncate` for a label, a chip and the scoreboard's
    rows (a status row that wraps is not a status row), and `verbatim` for output
    that already has columns and must not be re-flowed.

    A newline inside a span is a new logical line, handled here rather than at
    the nine callers that hold text a harness wrote: everything the mirror draws
    is somebody else's multi-line string, and a wrap that counted "a\\nb" as three
    columns would mis-lay every one of them.

    Returns:
        Result items.

    """
    content = list(spans)
    first = list(options.prefix)
    rest = list(first if options.continuation is None else options.continuation)
    has_multiple_lines = any("\n" in span.text for span in content)
    if options.mode != VERBATIM_LAYOUT and has_multiple_lines:
        return _multiline_rows(content, width, first, rest, options)
    if options.mode == VERBATIM_LAYOUT:
        return [_painted(first + content, width, options.background)]
    if options.mode == TRUNCATE_LAYOUT:
        truncated = _take(first + content, width).taken
        return [_painted(truncated, width, options.background)]
    return _WrapState.from_content(content, first, rest, width, options.background).paint()


def _multiline_rows(
    content: list[Span],
    width: int,
    first: list[Span],
    rest: list[Span],
    options: _RowOptions,
) -> list[str]:
    painted: list[str] = []
    for index, logical in enumerate(_split_lines(content)):
        painted.extend(
            rows(
                logical,
                width,
                _RowOptions(
                    prefix=tuple(first if index == 0 else rest),
                    continuation=tuple(rest),
                    mode=options.mode,
                    background=options.background,
                ),
            ),
        )
    return painted
