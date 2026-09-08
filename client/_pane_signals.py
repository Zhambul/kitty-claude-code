# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide terminal pane signal operations."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

import _handoff

if TYPE_CHECKING:
    import types


class _PaneSignalsContext(Protocol):
    kind: str
    session_id: str
    _opened: frozenset[str]

    def paint(self) -> None:
        """Paint the pane."""


class PaneSignals:
    """Provide terminal pane signal operations."""

    def ticked(self: _PaneSignalsContext, _signal_number: int = 0, _frame: types.FrameType | None = None) -> None:
        """Paint the changed scoreboard clock."""
        self.paint()

    def expanded(self: _PaneSignalsContext, _signal_number: int = 0, _frame: types.FrameType | None = None) -> None:
        """Reload expanded item state and paint."""
        self._opened = _handoff.opened(self.session_id, self.kind)
        self.paint()

    def resized(self: _PaneSignalsContext, _signal_number: int = 0, _frame: types.FrameType | None = None) -> None:
        """Paint the resized terminal."""
        self.paint()
