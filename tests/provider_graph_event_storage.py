# Copyright (c) 2026 Zhambyl Yermagambet
"""Provider graph access to event storage."""

from __future__ import annotations

from typing import TYPE_CHECKING

from repository.impl.sqlite.canonical_events import SqliteCanonicalEventRepository
from repository.impl.sqlite.connection import SqliteDatabase
from repository.impl.sqlite.raw_events import SqliteRawEventRepository
from repository.impl.sqlite.session_data import SqliteSessionDataRepository
from repository.impl.sqlite.sessions import SqliteSessionRepository
from tests.provider_graph_context import ProviderGraphContext

if TYPE_CHECKING:
    from repository.contract.facts import CanonicalEventRepository, RawEventRepository
    from repository.contract.session_data import SessionDataRepository
    from repository.contract.sessions import SessionRepository


class ProviderGraphEventStorage(ProviderGraphContext):
    """Provide event and session storage access."""

    @property
    def sessions(self) -> SessionRepository:
        """The session repository."""
        return self.provider("sessions", SqliteSessionRepository)

    @property
    def canonical_events(self) -> CanonicalEventRepository:
        """The canonical event repository."""
        return self.provider("canonical_events", SqliteCanonicalEventRepository)

    @property
    def raw_events(self) -> RawEventRepository:
        """The raw event repository."""
        return self.provider("raw_events", SqliteRawEventRepository)

    @property
    def session_data(self) -> SessionDataRepository:
        """The session data repository."""
        return self.provider("session_data", SqliteSessionDataRepository)

    @property
    def main_db(self) -> SqliteDatabase:
        """The main database."""
        return self.provider("main_db", SqliteDatabase)
