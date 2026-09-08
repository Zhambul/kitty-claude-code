# Copyright (c) 2026 Zhambyl Yermagambet
"""Split terminal mirror rendering."""

from __future__ import annotations

import re

from _render_diff_models import (
    _DiffParseState,
    _DiffRow,
    _mark_changed_pair,
)
from _render_styles import (
    REMOVED_DIFF_ROW,
)

_DIFF_HUNK = re.compile(r"^@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@")


def _diff_rows(unified_diff: str) -> list[_DiffRow]:
    parsed = _parsed_diff_rows(unified_diff)
    _mark_changed_diff_ranges(parsed)
    return parsed


def _parsed_diff_rows(unified_diff: str) -> list[_DiffRow]:
    parsed: list[_DiffRow] = []
    state = _DiffParseState()
    for line in unified_diff.splitlines():
        _parse_diff_input_line(parsed, state, line)
    return parsed


def _parse_diff_input_line(parsed: list[_DiffRow], state: _DiffParseState, line: str) -> None:
    hunk = _DIFF_HUNK.match(line)
    if hunk:
        if state.old_number is not None:
            parsed.append(_DiffRow("sep", None, "⋮"))
        state.old_number = int(hunk.group(1))
        state.new_number = int(hunk.group(2))
        return
    if _is_diff_metadata(line, state):
        return
    row = _parsed_diff_line(line, state)
    if row is not None:
        parsed.append(row)


def _is_diff_metadata(line: str, state: _DiffParseState) -> bool:
    return (
        state.old_number is None
        or state.new_number is None
        or line.startswith(("--- ", "+++ "))
        or line == r"\ No newline at end of file"
    )


def _parsed_diff_line(line: str, state: _DiffParseState) -> _DiffRow | None:
    old_number = state.old_number
    new_number = state.new_number
    if old_number is None or new_number is None:
        return None
    if line.startswith("-"):
        state.old_number = old_number + 1
        return _DiffRow(REMOVED_DIFF_ROW, old_number, line[1:])
    if line.startswith("+"):
        state.new_number = new_number + 1
        return _DiffRow("added", new_number, line[1:])
    if line.startswith(" "):
        state.old_number = old_number + 1
        state.new_number = new_number + 1
        return _DiffRow("context", new_number, line[1:])
    return None


def _mark_changed_diff_ranges(parsed: list[_DiffRow]) -> None:
    index = 0
    while index < len(parsed):
        if parsed[index].kind != REMOVED_DIFF_ROW:
            index += 1
            continue
        removed_start = index
        index = _diff_block_end(parsed, index, REMOVED_DIFF_ROW)
        added_start = index
        index = _diff_block_end(parsed, index, "added")
        for offset in range(min(added_start - removed_start, index - added_start)):
            _mark_changed_pair(parsed, removed_start + offset, added_start + offset)


def _diff_block_end(parsed: list[_DiffRow], start: int, kind: str) -> int:
    index = start
    while index < len(parsed) and parsed[index].kind == kind:
        index += 1
    return index
