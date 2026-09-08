# Copyright (c) 2026 Zhambyl Yermagambet
"""Verify the typed SDK client."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from api.sessiondata.models.session_data import SessionDataListResponse
from sdk import sse
from sdk.client import (
    SessionRef,
    SessionsResource,
)
from sdk.transport import ApiFailureError
from tests.sdk_test_resources import sessions_resource
from tests.sdk_test_support import (
    message_entry,
    session_data,
)
from tests.sdk_test_transports import (
    InvalidPageTransport,
    PagedTransport,
    StalledTransport,
)

if TYPE_CHECKING:
    from sdk.state import SessionSnapshot

NEXT_CURSOR = 1_002
SNAPSHOT_REQUEST_COUNT = 3
SNAPSHOT_PAGE_COUNT = 2


SESSION_ID_TEXT = "session-one"


SESSION = SessionRef(SESSION_ID_TEXT)


class PromptOwnerSessions(SessionsResource):
    """Represent prompt owner sessions."""

    def __init__(self, snapshots: dict[str, SessionSnapshot]) -> None:
        """Store session snapshots by identifier."""
        self.snapshots = snapshots

    def list(self) -> SessionDataListResponse:
        """Return list.

        Returns:
            List.

        """
        return SessionDataListResponse(
            cursor=max(snapshot.cursor for snapshot in self.snapshots.values()),
            sessions=tuple(snapshot.session_data for snapshot in self.snapshots.values()),
        )

    def snapshot(self, session: SessionRef) -> SessionSnapshot:
        """Return snapshot.

        Returns:
            Snapshot.

        """
        return self.snapshots[session.session_id]


def test_session_snapshot_reads_all_pages_at_one() -> None:
    """Verify a session snapshot reads all pages at one cursor."""
    transport = PagedTransport()
    sessions = sessions_resource(transport)

    snapshot = sessions.snapshot(SESSION)

    assert [entry.cursor for entry in snapshot.entries] == list(range(1, NEXT_CURSOR))
    assert len(transport.paths) == SNAPSHOT_REQUEST_COUNT


def test_session_snapshot_read_reports_its_page() -> None:
    """Verify a session snapshot read reports its page count."""
    sessions = sessions_resource(PagedTransport())

    result = sessions.read_snapshot(SESSION)

    assert result.page_count == SNAPSHOT_PAGE_COUNT


def test_session_snapshot_rejects_repeated_entry() -> None:
    """Verify a session snapshot rejects a repeated entry."""
    repeated = message_entry(1)
    sessions = sessions_resource(InvalidPageTransport(session_data(1), (repeated, repeated)))

    with pytest.raises(ApiFailureError, match="repeated entry id"):
        sessions.snapshot(SESSION)


def test_session_snapshot_rejects_entry_newer() -> None:
    """Verify a session snapshot rejects an entry newer than its cursor."""
    sessions = sessions_resource(InvalidPageTransport(session_data(1), (message_entry(2),)))

    with pytest.raises(ApiFailureError, match="newer than snapshot cursor 1"):
        sessions.snapshot(SESSION)


def test_session_snapshot_rejects_page_that() -> None:
    """Verify a session snapshot rejects a page that cannot make progress."""
    sessions = sessions_resource(StalledTransport())

    with pytest.raises(ApiFailureError, match="returned no entries"):
        sessions.snapshot(SESSION)


def test_sse_parser_reads_comments_and_multiline() -> None:
    """Verify the SSE parser reads comments and multiline data."""
    found = tuple(
        sse.events(
            [
                ": heartbeat",
                "event: sample",
                "id: 17",
                "data: first",
                "data: second",
                "",
            ],
        ),
    )

    assert found == (sse.SseEvent("sample", "17", "first\nsecond"),)
