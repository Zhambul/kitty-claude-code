# Copyright (c) 2026 Zhambyl Yermagambet
"""Database runtime for canonical record tests."""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING

from repository.impl.sqlite import (
    canonical_events,
    connection,
    databases,
    raw_event_audits,
    raw_events,
    sessions,
    shell_output,
    workspace,
)

if TYPE_CHECKING:
    from domain.event_base import CanonicalEvent, EventPayload
    from domain.ids import HarnessName
    from harness.models.raw_events import RawEvent, TranslationResult
    from harness.models.session import Session
    from harness.registry import HarnessRegistry

RAW_EVENT_BACKLOG_LIMIT = 1_000_000


@dataclass(init=False, repr=False, eq=False)
class CanonicalRuntime:
    """Store and translate canonical test records in one database."""

    database_path: str
    database: connection.SqliteDatabase
    clock: Callable[[], float]
    store: canonical_events.SqliteCanonicalEventRepository
    recorder: raw_events.SqliteRawEventRepository
    sessions: sessions.SqliteSessionRepository
    shell_output: shell_output.SqliteShellOutputRepository
    raw_event_audits: raw_event_audits.SqliteRawEventAuditRepository
    workspaces: workspace.SqliteSessionWorkspaceRepository

    def __init__(
        self,
        database_path: str,
        clock: Callable[[], float] = time.time,
        harnesses: HarnessRegistry | None = None,
    ) -> None:
        """Initialize the runtime."""
        self.database_path = str(database_path)
        self.database = databases.main_database(self.database_path)
        self.clock = clock
        self.store = canonical_events.SqliteCanonicalEventRepository(self.database)
        self.recorder = raw_events.SqliteRawEventRepository(self.database)
        self.sessions = sessions.SqliteSessionRepository(self.database, harnesses)
        self.shell_output = shell_output.SqliteShellOutputRepository(self.database)
        self.raw_event_audits = raw_event_audits.SqliteRawEventAuditRepository(self.database)
        self.workspaces = workspace.SqliteSessionWorkspaceRepository(self.database)

    def register(self, harness: HarnessName, session: Session) -> None:
        """Register one harness session."""
        self.sessions.save(harness, session)

    def record(
        self,
        raw_event: RawEvent,
        translator_version: str,
        translation: TranslationResult,
    ) -> tuple[CanonicalEvent[EventPayload], ...]:
        """Record one raw event and its translation.

        Returns:
            The accepted canonical events, or an empty tuple for a repeated raw event.

        """
        self.recorder.record((raw_event,))
        backlog = {raw.raw_event_id for raw in self.recorder.unverdicted(RAW_EVENT_BACKLOG_LIMIT)}
        if raw_event.raw_event_id not in backlog:
            return ()
        outcome = self.store.record_translation(raw_event, translator_version, translation, self.clock())
        return outcome.accepted
