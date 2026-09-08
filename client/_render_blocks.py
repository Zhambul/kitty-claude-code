# Copyright (c) 2026 Zhambyl Yermagambet
"""Split terminal mirror rendering."""

from __future__ import annotations

from dataclasses import dataclass

from _render_rows import (
    _RowOptions,
    rows,
)
from _render_styles import (
    DARK,
    TEXT_INDENT,
    TRUNCATE_LAYOUT,
    Color,
    Span,
)
from _render_tasks import _rule


@dataclass(frozen=True)
class _BlockContent:
    summary: str
    output: str
    status: str
    finish: list[Span] | None
    links: list[Span] | None = None


def _block(
    chip: str,
    chip_color: Color,
    content: _BlockContent,
    width: int,
) -> list[str]:
    """Return the block.

    The command shape: a chip and what was asked for, then what came back
        behind a rail, then how it ended. Every tool that produces output uses it —
        a search and a shell differ in their chip and in nothing else.

    Returns:
        Block.

    """
    heading = _block_heading(chip, chip_color, content.links)
    heading_rows = rows(heading, width, _RowOptions(mode=TRUNCATE_LAYOUT))
    painted = ["", _rule(width), *heading_rows]
    if content.summary:
        painted.extend(_block_summary_rows(content.summary, width))
    painted.append(_rule(width))
    painted.extend(_block_stream_rows(content, chip_color, width))
    if content.finish is not None:
        painted.append(_rule(width))
        painted.extend(rows(content.finish, width, _RowOptions(mode=TRUNCATE_LAYOUT)))
        painted.append(_rule(width))
    return painted


def _block_summary_rows(summary: str, width: int) -> list[str]:
    return rows(
        [Span(summary)],
        width,
        _RowOptions(continuation=(Span(TEXT_INDENT),)),
    )


def _block_heading(
    chip: str,
    chip_color: Color,
    links: list[Span] | None,
) -> list[Span]:
    heading = [Span(f" {chip} ", DARK, chip_color, bold=True)]
    for index, link in enumerate(links or ()):
        heading.extend((Span(TEXT_INDENT if index == 0 else " "), link))
    return heading


def _block_stream_rows(
    content: _BlockContent,
    chip_color: Color,
    width: int,
) -> list[str]:
    painted: list[str] = []
    rail = (Span("│ ", chip_color),)
    for stream in (content.status, content.output):
        for line in stream.splitlines():
            painted.extend(
                rows(
                    [Span(line.rstrip())],
                    width,
                    _RowOptions(prefix=rail, continuation=rail),
                ),
            )
    return painted
