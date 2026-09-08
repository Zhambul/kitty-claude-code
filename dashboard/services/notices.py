# Copyright (c) 2026 Zhambyl Yermagambet
"""The newest thing worth telling you about, and nothing older.

One notice at a time, with a revision number. There is no queue and no
subscription: a client that reconnects wants the CURRENT notice, and a client
that already saw revision N wants to know only whether there is an N+1.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass
from typing import TYPE_CHECKING

from domain.ids import SessionId

if TYPE_CHECKING:
    from collections.abc import Callable


@dataclass(frozen=True)
class DashboardNotificationNotice:
    """Represent dashboard notification notice."""

    revision: int
    session_id: SessionId
    kind: str
    project: str
    title: str


class DashboardNotificationState:
    """Hold only the latest current notices; there are no subscriptions or queues."""

    def __init__(self, changed: Callable[[], None] | None = None) -> None:
        """Initialize the object."""
        self._lock = threading.Lock()
        self._revision = 0
        self._notification: DashboardNotificationNotice | None = None
        self.changed = changed

    def publish_notification(
        self,
        session_id: SessionId,
        kind: str,
        project: str,
        title: str,
    ) -> None:
        """Publish notification."""
        with self._lock:
            self._revision += 1
            self._notification = DashboardNotificationNotice(
                self._revision,
                session_id,
                kind,
                project,
                title,
            )
        if self.changed is not None:
            self.changed()

    def notification(self) -> DashboardNotificationNotice | None:
        """Return the notification.

        Returns:
            Notification.

        """
        with self._lock:
            return self._notification
