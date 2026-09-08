# Copyright (c) 2026 Zhambyl Yermagambet
"""Split terminal mirror rendering."""

from __future__ import annotations

from dataclasses import dataclass
from typing import NamedTuple


class _DiffRow(NamedTuple):
    kind: str
    number: int | None
    text: str
    changed: _TextRange | None = None


@dataclass
class _DiffParseState:
    old_number: int | None = None
    new_number: int | None = None


class _TextRange(NamedTuple):
    start: int
    end: int


class _ChangedRanges(NamedTuple):
    removed: _TextRange
    added: _TextRange


def _changed_ranges(before: str, after: str) -> _ChangedRanges:
    prefix = 0
    limit = min(len(before), len(after))
    while prefix < limit and before[prefix] == after[prefix]:
        prefix += 1
    suffix = 0
    remaining = min(len(before) - prefix, len(after) - prefix)
    while suffix < remaining:
        if before[-suffix - 1] != after[-suffix - 1]:
            break
        suffix += 1
    return _ChangedRanges(
        _TextRange(prefix, len(before) - suffix),
        _TextRange(prefix, len(after) - suffix),
    )


def _mark_changed_pair(
    parsed: list[_DiffRow],
    removed_index: int,
    added_index: int,
) -> None:
    removed_range, added_range = _changed_ranges(
        parsed[removed_index].text,
        parsed[added_index].text,
    )
    parsed[removed_index] = parsed[removed_index]._replace(changed=removed_range)
    parsed[added_index] = parsed[added_index]._replace(changed=added_range)
