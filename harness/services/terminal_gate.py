# Copyright (c) 2026 Zhambyl Yermagambet
"""One terminal operation at a time for each session."""

from __future__ import annotations

import threading
from contextlib import contextmanager
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from _thread import LockType
    from collections.abc import Iterator

    from domain.ids import SessionId


class SessionTerminalGate:
    """Represent session terminal gate."""

    def __init__(self) -> None:
        """Initialize the object."""
        self._guard = threading.Lock()
        self._locks: dict[SessionId, LockType] = {}

    @contextmanager
    def enter(self, session_id: SessionId) -> Iterator[None]:
        """Return the enter."""
        with self._guard:
            lock = self._locks.setdefault(session_id, threading.Lock())
        with lock:
            yield
