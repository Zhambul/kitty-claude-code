# Copyright (c) 2026 Zhambyl Yermagambet
"""Wait for process exit and open file writes with native notifications."""

import contextlib
import os
import select
import selectors
import socket
from collections.abc import Callable
from pathlib import Path
from threading import Event, Thread

from core.process_subscriptions import ProcessSubscriptions


class KernelEvents:
    """Use kqueue on macOS and process descriptors on Linux."""

    def __init__(self, changed: Callable[[], None]) -> None:
        """Set up the blocking wait and its stop signal."""
        self._changed = changed
        reader, writer = socket.socketpair()
        self._reader = reader
        self._writer = writer
        self._selector = selectors.DefaultSelector()
        self._selector.register(self._reader, selectors.EVENT_READ)
        self._queue = select.kqueue() if hasattr(select, "kqueue") else None
        if self._queue is not None:
            self._selector.register(self._queue, selectors.EVENT_READ)
        self._processes = ProcessSubscriptions(self._selector, self._queue, changed)
        self._files: dict[Path, tuple[int, int]] = {}
        self._stopping = Event()
        self._thread = Thread(target=self._run, name="baqylau-process-events", daemon=True)

    def start(self) -> None:
        """Start the blocking kernel wait."""
        self._thread.start()

    def update(self, process_ids: set[int]) -> None:
        """Replace process subscriptions without a gap in exit detection."""
        self._processes.update(process_ids)

    def update_files(self, paths: set[Path]) -> bool:
        """Watch open files on macOS; Linux uses the directory observer.

        Returns:
            True if a file watch was added.

        """
        if self._queue is None:
            return False
        added = False
        for path in self._files.keys() - paths:
            os.close(self._files.pop(path)[0])
        for path in paths:
            with contextlib.suppress(FileNotFoundError):
                added = self._watch_file(path) or added
        return added

    def close(self) -> None:
        """Wake the kernel wait and release descriptors."""
        self._stopping.set()
        self._writer.send(b"x")
        self._thread.join()
        self._processes.close()
        for descriptor, _inode in self._files.values():
            os.close(descriptor)
        self._selector.close()
        if self._queue is not None:
            self._queue.close()
        for connection in (self._reader, self._writer):
            connection.close()

    def _run(self) -> None:
        while not self._stopping.is_set():
            for key, _mask in self._selector.select():
                if key.fileobj is self._reader:
                    return
                if self._queue is None:
                    self._selector.unregister(key.fileobj)
                else:
                    self._queue.control(
                        None,
                        max(1, len(self._processes.process_ids) + len(self._files)),
                        0,
                    )
                self._changed()

    def _watch_file(self, path: Path) -> bool:
        if self._queue is None:
            return False
        inode = path.stat().st_ino
        previous = self._files.get(path)
        if previous is not None and previous[1] == inode:
            return False
        if previous is not None:
            os.close(self._files.pop(path)[0])
        descriptor = os.open(path, os.O_RDONLY)
        event = select.kevent(
            descriptor,
            filter=select.KQ_FILTER_VNODE,
            flags=select.KQ_EV_ADD | select.KQ_EV_CLEAR,
            fflags=select.KQ_NOTE_WRITE | select.KQ_NOTE_EXTEND | select.KQ_NOTE_DELETE | select.KQ_NOTE_RENAME,
        )
        try:
            self._queue.control([event], 0)
        except OSError:
            os.close(descriptor)
            raise
        self._files[path] = (descriptor, os.fstat(descriptor).st_ino)
        return True
