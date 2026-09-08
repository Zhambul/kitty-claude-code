# Copyright (c) 2026 Zhambyl Yermagambet
"""Split SDK client implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from collections.abc import Callable

    from sdk import state
    from sdk.client_models import SessionRef

from sdk.client_wait import wait_for


class _SessionSnapshotReader(Protocol):
    """Read one session snapshot."""

    def snapshot(self, session: SessionRef) -> state.SessionSnapshot:
        """Return the session snapshot."""
        ...


class SessionWatch:
    """Represent session watch."""

    def __init__(self, sessions: _SessionSnapshotReader, session: SessionRef) -> None:
        """Initialize the session watch."""
        self.sessions = sessions
        self.session = session
        self.last_snapshot: state.SessionSnapshot | None = None

    def snapshot(self) -> state.SessionSnapshot:
        """Return snapshot.

        Returns:
            Snapshot.

        """
        self.last_snapshot = self.sessions.snapshot(self.session)
        return self.last_snapshot

    def wait[WatchResultT](
        self,
        description: str | Callable[[state.SessionSnapshot], str],
        condition: Callable[[state.SessionSnapshot], WatchResultT | None],
        *,
        timeout: float,
    ) -> WatchResultT:
        """Wait.

        Returns:
            The t.

        """
        return wait_for(
            lambda: self._wait_description(description),
            lambda: self._read_snapshot_condition(condition),
            timeout=timeout,
        )

    def _read_snapshot_condition[WatchResultT](
        self,
        condition: Callable[[state.SessionSnapshot], WatchResultT | None],
    ) -> WatchResultT | None:
        return condition(self.snapshot())

    def _wait_description(
        self,
        description: str | Callable[[state.SessionSnapshot], str],
    ) -> str:
        snapshot = self.last_snapshot or self.snapshot()
        return description(snapshot) if callable(description) else description
