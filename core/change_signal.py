# Copyright (c) 2026 Zhambyl Yermagambet
"""Wake readers when a writer commits changed data."""

from __future__ import annotations

import asyncio
import contextlib
from dataclasses import dataclass
from threading import Event as ThreadEvent, Lock
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator


@dataclass(frozen=True)
class _Reader:
    loop: asyncio.AbstractEventLoop
    ready: asyncio.Event


class ChangeSignal:
    """Combine repeated notices for each connected reader."""

    def __init__(self) -> None:
        """Create a signal with no readers."""
        self._lock = Lock()
        self._readers: set[_Reader] = set()
        self._thread_readers: set[ThreadEvent] = set()
        self._batches = 0
        self._pending = False

    @contextlib.contextmanager
    def batch(self) -> Iterator[None]:
        """Send one notice after a group of committed changes.

        Yields:
            Control to the writer.

        """
        with self._lock:
            self._batches += 1
        try:
            yield
        finally:
            with self._lock:
                self._batches -= 1
                publish = self._batches == 0 and self._pending
                if publish:
                    self._pending = False
            if publish:
                self.publish()

    @contextlib.contextmanager
    def subscribe_thread(self) -> Iterator[ThreadEvent]:
        """Register a worker before its first read.

        Yields:
            The worker's change event.

        """
        ready = ThreadEvent()
        with self._lock:
            self._thread_readers.add(ready)
        try:
            yield ready
        finally:
            with self._lock:
                self._thread_readers.remove(ready)

    @contextlib.contextmanager
    def subscribe(self) -> Iterator[asyncio.Event]:
        """Register before the first read and release on disconnect.

        Yields:
            The reader's change event.

        """
        reader = _Reader(asyncio.get_running_loop(), asyncio.Event())
        with self._lock:
            self._readers.add(reader)
        try:
            yield reader.ready
        finally:
            with self._lock:
                self._readers.remove(reader)

    def publish(self) -> None:
        """Notify readers from the writer's thread."""
        with self._lock:
            if self._batches:
                self._pending = True
                return
            readers = tuple(self._readers)
            thread_readers = tuple(self._thread_readers)
        for ready in thread_readers:
            ready.set()
        for reader in readers:
            # A disconnected reader can close its loop after this snapshot.
            with contextlib.suppress(RuntimeError):
                reader.loop.call_soon_threadsafe(reader.ready.set)
