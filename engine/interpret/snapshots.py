# Copyright (c) 2026 Zhambyl Yermagambet
"""Cache terminal windows for fast interpreter ticks."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from collections.abc import Callable

    from harness.contract import TerminalWindows

TERMINAL_SNAPSHOT_INTERVAL_SECONDS = 1.0


class TerminalWindowReader(Protocol):
    """Read terminal windows for liveness checks."""

    def windows(self) -> TerminalWindows:
        """Return terminal windows."""
        ...


class TerminalSnapshotCache(Protocol):
    """Cache terminal windows for interpreter ticks."""

    def sample(self) -> TerminalWindows:
        """Return cached terminal windows."""
        ...

    def invalidate(self) -> None:
        """Invalidate the cached terminal windows."""
        ...


class TerminalSnapshotSampler(TerminalSnapshotCache):
    """Use one terminal snapshot for several fast ticks."""

    def __init__(
        self,
        terminal_window_reader: TerminalWindowReader | None,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        """Initialize the sampler."""
        self._terminal = terminal_window_reader
        self._clock = clock
        self._sampled_at: float | None = None
        self._windows: TerminalWindows = ()

    def sample(self) -> TerminalWindows:
        """Return the current cached snapshot.

        Returns:
            The terminal windows.

        """
        if self._terminal is None:
            return ()
        now = self._clock()
        if self._sampled_at is None or now - self._sampled_at >= TERMINAL_SNAPSHOT_INTERVAL_SECONDS:
            self._windows = self._terminal.windows()
            self._sampled_at = now
        return self._windows

    def invalidate(self) -> None:
        """Make the next sample read the terminal again."""
        self._sampled_at = None
