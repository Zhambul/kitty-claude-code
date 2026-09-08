# Copyright (c) 2026 Zhambyl Yermagambet
"""Shared parsing and selection for Claude Code numbered menus."""

from __future__ import annotations

import re
import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass

from domain.ids import WindowId
from harness.impl.claude_code.controls.screen_protocols import ScreenDriver

_ROW = re.compile(
    r"^\s*(?P<marks>(?:[\u276f↑↓]\s*)*)(?P<digit>\d+)\.\s+(?P<label>.+?)\s*$",
)
KEY_EFFECT_TIMEOUT_SECONDS = 2.0


@dataclass(frozen=True)
class Row:
    """Represent row."""

    digit: str
    label: str
    cursor: bool


class SelectionError(RuntimeError):
    """Represent selection error."""


@dataclass(frozen=True)
class SelectionContext:
    """Hold the terminal operations for one menu selection."""

    screen_driver: ScreenDriver
    window_id: WindowId
    read_rows: Callable[[], Sequence[Row]]
    sleep: Callable[[float], None]
    key_gap: float


def rows(text: str) -> tuple[Row, ...]:
    """Return the rows.

    Returns:
        Rows.

    """
    found: list[Row] = []
    for line in (text or "").splitlines():
        match = _ROW.match(line)
        if match is not None:
            found.append(
                Row(
                    match.group("digit"),
                    match.group("label").strip(),
                    "\u276f" in match.group("marks"),
                ),
            )
    return tuple(found)


def select(
    selection_context: SelectionContext,
    digit: str,
) -> None:
    """Move to one verified row and press Enter.

    The selector raises SelectionError if it cannot verify the target row.

    """
    _Selector(selection_context, digit).run()


class _Selector:
    def __init__(self, selection_context: SelectionContext, digit: str) -> None:
        self.context = selection_context
        self.digit = digit

    def run(self) -> None:
        options = tuple(self.context.read_rows())
        target_index, current_index = self._positions(options)
        key = "down" if target_index > current_index else "up"
        remaining_moves = abs(target_index - current_index)
        while remaining_moves:
            self._move(key)
            remaining_moves -= 1
        self._confirm()
        self.context.screen_driver.send_key(self.context.window_id, "enter")

    def _positions(self, options: tuple[Row, ...]) -> tuple[int, int]:
        target_index = next(
            (index for index, option in enumerate(options) if option.digit == self.digit),
            None,
        )
        current_index = next(
            (index for index, option in enumerate(options) if option.cursor),
            None,
        )
        if target_index is None or current_index is None:
            message = "the cursor or target option is absent"
            raise SelectionError(message)
        return target_index, current_index

    def _move(self, key: str) -> None:
        before = self._cursor_digit()
        if not self.context.screen_driver.send_key(self.context.window_id, key):
            message = "the cursor key was not delivered"
            raise SelectionError(message)
        deadline = time.monotonic() + KEY_EFFECT_TIMEOUT_SECONDS
        while self._cursor_digit() in {None, before}:
            if time.monotonic() >= deadline:
                message = "the cursor key had no visible effect"
                raise SelectionError(message)
            self.context.sleep(self.context.key_gap)

    def _confirm(self) -> None:
        selected = next(
            (option for option in self.context.read_rows() if option.cursor),
            None,
        )
        if selected is None or selected.digit != self.digit:
            message = "the target option did not get the cursor"
            raise SelectionError(message)

    def _cursor_digit(self) -> str | None:
        return next(
            (option.digit for option in self.context.read_rows() if option.cursor),
            None,
        )
