# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide terminal pane state-update operations."""

from __future__ import annotations

import contextlib
from typing import Protocol

import _model


class _PaneStateContext(Protocol):
    model: _model.SessionModel
    _busy: bool
    _resized: bool

    def paint(self) -> None:
        """Paint the pane."""

    def _busy_state(self) -> contextlib.ExitStack:
        """Keep the pane busy for one update."""


class PaneState:
    """Provide terminal pane state-update operations."""

    def apply(self: _PaneStateContext, event: str, event_payload: str) -> None:
        """Apply one event and paint the new state."""
        with self._busy_state():
            if event == "sessionData":
                self.model.apply_frame(_model.StreamFrameDocument.model_validate_json(event_payload))
        self.paint()

    def deferred_repaint(self: _PaneStateContext) -> None:
        """Paint a resize that arrived during an update."""
        if self._resized:
            self.paint()

    def _busy_state(self: _PaneStateContext) -> contextlib.ExitStack:
        """Keep the pane busy for one state update.

        Returns:
            A cleanup context that clears the busy flag when the update ends.

        """
        self._busy = True
        cleanup = contextlib.ExitStack()
        cleanup.callback(setattr, self, "_busy", False)  # noqa: FBT003 -- setattr only accepts positional arguments.
        return cleanup
