# Copyright (c) 2026 Zhambyl Yermagambet
"""Split terminal mirror rendering."""

from __future__ import annotations

from typing import TYPE_CHECKING

from _render_numbers import count
from _render_styles import (
    FAILURE,
    MUTED,
    PRIMARY_TEXT,
    SUCCESS,
    WORKING,
    _ScorePart,
)

if TYPE_CHECKING:
    from _model import (
        TokenRecord,
    )
    from _render_statistics import SessionStatistics


def _score_usage(tokens: TokenRecord, cost: float | None) -> list[_ScorePart]:
    cache_write = tokens.cache_write_tokens + tokens.one_hour_cache_write_tokens
    total = tokens.input_tokens + tokens.output_tokens + tokens.cache_read_tokens + cache_write
    usage_parts = [_ScorePart(f"{count(total)} total", PRIMARY_TEXT)]
    for token_count, label in (
        (tokens.input_tokens, "in"),
        (tokens.output_tokens, "out"),
        (tokens.cache_read_tokens, "cache"),
        (cache_write, "write"),
    ):
        if token_count:
            usage_parts.append(_ScorePart(f"{count(token_count)} {label}", MUTED))
    if cost is not None:
        usage_parts.append(_ScorePart(f"≈ ${cost:.2f}", WORKING))
    return usage_parts


def _score_detail(statistics: SessionStatistics) -> list[_ScorePart]:
    detail: list[_ScorePart] = []
    if statistics.file_count:
        noun = "file" if statistics.file_count == 1 else "files"
        detail.append(_ScorePart(f"{int(statistics.file_count)} {noun}", MUTED))
    if statistics.lines_added:
        detail.append(_ScorePart(f"+{int(statistics.lines_added)}", SUCCESS))
    if statistics.lines_removed:
        detail.append(_ScorePart(f"-{int(statistics.lines_removed)}", FAILURE))
    detail.extend(
        _ScorePart(f"{tool} {int(tool_count)}", MUTED)
        for tool, tool_count in sorted(
            statistics.tool_counts.items(),
            key=_tool_sort_key,
        )
    )
    return detail


def _tool_sort_key(tool_statistic: tuple[str, int]) -> tuple[int, str]:
    return -tool_statistic[1], tool_statistic[0].lower()
