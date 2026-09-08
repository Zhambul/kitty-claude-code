# Copyright (c) 2026 Zhambyl Yermagambet
"""The revision of browser application state.

The global event stream reads this small value after a change notice. It reads the
application snapshot only when a producer advances the revision.
"""

from __future__ import annotations

import threading

from core.change_signal import ChangeSignal


class ApplicationUpdateState:
    """One process-wide revision for state in ``/api/application``."""

    def __init__(self) -> None:
        """Initialize the object."""
        self._lock = threading.Lock()
        self._revision = 0
        self.changes = ChangeSignal()

    def publish(self) -> None:
        """Publish publish."""
        with self._lock:
            self._revision += 1
        self.changes.publish()

    def revision(self) -> int:
        """Return the revision.

        Returns:
            Revision.

        """
        with self._lock:
            return self._revision
