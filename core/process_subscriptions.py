# Copyright (c) 2026 Zhambyl Yermagambet
"""Own native process-exit subscriptions for a shared event selector."""

from __future__ import annotations

import contextlib
import os
import select
import selectors
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable


class ProcessSubscriptions:
    """Register process exits without owning the shared selector or kqueue."""

    def __init__(
        self,
        selector: selectors.BaseSelector,
        queue: select.kqueue | None,
        changed: Callable[[], None],
    ) -> None:
        """Store the event resources and the change callback."""
        self._selector = selector
        self._queue = queue
        self._changed = changed
        self.process_ids: set[int] = set()
        self._descriptors: dict[int, int] = {}

    def update(self, process_ids: set[int]) -> None:
        """Replace subscriptions and report processes that have already exited."""
        for pid in self.process_ids - process_ids:
            self._remove(pid)
        for pid in process_ids - self.process_ids:
            try:
                self._add(pid)
            except ProcessLookupError:
                self._changed()
        self.process_ids = process_ids

    def close(self) -> None:
        """Remove process subscriptions and close owned process descriptors."""
        for pid in tuple(self.process_ids):
            self._remove(pid)

    def _add(self, pid: int) -> None:
        if self._queue is None:
            if sys.platform == "linux":
                descriptor = os.pidfd_open(pid)
                self._descriptors[pid] = descriptor
                self._selector.register(descriptor, selectors.EVENT_READ, pid)
                return
            message = "Process events require macOS or Linux"
            raise NotImplementedError(message)
        event = select.kevent(
            pid,
            filter=select.KQ_FILTER_PROC,
            flags=select.KQ_EV_ADD | select.KQ_EV_ONESHOT,
            fflags=select.KQ_NOTE_EXIT,
        )
        self._queue.control([event], 0)

    def _remove(self, pid: int) -> None:
        if self._queue is None:
            descriptor = self._descriptors.pop(pid, None)
            if descriptor is not None:
                with contextlib.suppress(KeyError):
                    self._selector.unregister(descriptor)
                os.close(descriptor)
        else:
            with contextlib.suppress(ProcessLookupError, FileNotFoundError):
                self._queue.control(
                    [select.kevent(pid, filter=select.KQ_FILTER_PROC, flags=select.KQ_EV_DELETE)],
                    0,
                )
