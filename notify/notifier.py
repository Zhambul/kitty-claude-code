# Copyright (c) 2026 Zhambyl Yermagambet
"""Publish notifications from canonical session state."""

from __future__ import annotations

from contextlib import ExitStack
from typing import TYPE_CHECKING

from notify.notifier_dependencies import NotifierDependencies as NotifierDependencies
from notify.notifier_models import PendingNotification as PendingNotification
from notify.notifier_processing import NOTIFICATION_RETRY_SECONDS, _NotifierRetraction

if TYPE_CHECKING:
    import threading


class Notifier(_NotifierRetraction):
    """Publish and deliver transitions into canonical attention states."""

    def run(self, stop: threading.Event) -> None:
        """Wait for changed state, a delivery deadline, or a failed-delivery retry."""
        with ExitStack() as cleanup, self._changes.subscribe_thread() as changed:
            self._wake = changed
            cleanup.callback(setattr, self, "_wake", None)
            while not stop.is_set():
                changed.clear()
                delay = self._scan_or_retry()
                if stop.is_set():
                    return
                changed.wait(delay)

    def stop(self) -> None:
        """Release the worker wait after its stop event is set."""
        if self._wake is not None:
            self._wake.set()

    def _scan_or_retry(self) -> float | None:
        try:
            return self._scan_delay()
        except Exception:  # noqa: BLE001 -- Record delivery failures and keep the worker available for retries.
            self._audit.error("", "dashboard notifier")
            return NOTIFICATION_RETRY_SECONDS

    def _scan_delay(self) -> float | None:
        self.scan()
        return self._next_delay()
