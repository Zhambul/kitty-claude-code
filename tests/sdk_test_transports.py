# Copyright (c) 2026 Zhambyl Yermagambet
"""Verify the typed SDK client."""

from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING
from urllib.parse import parse_qs, urlsplit

from pydantic import BaseModel, TypeAdapter

from api.controls.models import control_outcome_response, control_request
from api.sessiondata.models import entry, session_data as session_data_models
from harness.models.controls import (
    ControlAcknowledgement,
)
from tests.sdk_test_support import (
    _transport_response,
    message_entry,
    session_data,
)

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator

    from sdk.state import SessionSnapshot


INITIAL_CURSOR = 1_001


NEXT_CURSOR = 1_002


PLAIN_TEXT_MEDIA_TYPE = "text/plain"


SESSION_DATA_PATH = "/sessionData/session-one"


type TransportPost = tuple[str, BaseModel, set[int]]


class PagedTransport:
    """Represent paged transport."""

    def __init__(self) -> None:
        """Create an empty page request record."""
        self.paths: list[str] = []

    def get[Response](self, path: str, _adapter: TypeAdapter[Response]) -> Response:
        """Return the requested fixture page.

        Returns:
            The requested fixture page.

        """
        self.paths.append(path)
        if path == SESSION_DATA_PATH:
            return _transport_response(_adapter, session_data())
        query = parse_qs(urlsplit(path).query)
        assert query["at"] == [str(INITIAL_CURSOR)]
        if "before" not in query:
            return _transport_response(
                _adapter,
                entry.EntryPageResponse(
                    items=tuple(message_entry(cursor) for cursor in range(2, NEXT_CURSOR)),
                    oldest_cursor=2,
                    has_more=True,
                ),
            )
        assert query["before"] == ["2"]
        return _transport_response(
            _adapter,
            entry.EntryPageResponse(items=(message_entry(1),), oldest_cursor=1, has_more=False),
        )


class FixedWatch:
    """Represent fixed watch."""

    def __init__(self, snapshot: SessionSnapshot) -> None:
        """Store one fixed session snapshot."""
        self.snapshot = snapshot
        self.timeout: float | None = None

    def wait[Result](
        self,
        _description: str,
        condition: Callable[[SessionSnapshot], Result],
        *,
        timeout: float,
    ) -> Result:
        """Record the timeout and check the fixed snapshot once.

        Returns:
            The condition result without waiting or retrying.

        """
        self.timeout = timeout
        return condition(self.snapshot)


class StalledTransport:
    """Represent stalled transport."""

    def get[Response](self, path: str, _adapter: TypeAdapter[Response]) -> Response:
        """Return a page that never completes.

        Returns:
            A page that never completes.

        """
        if path == SESSION_DATA_PATH:
            return _transport_response(_adapter, session_data())
        return _transport_response(_adapter, entry.EntryPageResponse(items=(), oldest_cursor=0, has_more=True))


class InvalidPageTransport:
    """Represent invalid page transport."""

    def __init__(
        self, session_snapshot: session_data_models.SessionDataResponse, entries: tuple[entry.EntryResponse, ...],
    ) -> None:
        """Store one invalid page fixture."""
        self.session_snapshot = session_snapshot
        self.entries = entries

    def get[Response](self, path: str, _adapter: TypeAdapter[Response]) -> Response:
        """Return the invalid page fixture.

        Returns:
            The invalid page fixture.

        """
        if path == SESSION_DATA_PATH:
            return _transport_response(_adapter, self.session_snapshot)
        return _transport_response(
            _adapter,
            entry.EntryPageResponse(
                items=self.entries,
                oldest_cursor=min((entry.cursor for entry in self.entries), default=0),
                has_more=False,
            ),
        )


class EventStreamTransport:
    """Represent event stream transport."""

    def __init__(self, lines: list[str]) -> None:
        """Store event-stream lines."""
        self.lines = lines
        self.requests: list[tuple[str, dict[str, str] | None]] = []

    @contextmanager
    def event_stream(
        self,
        path: str,
        *,
        headers: dict[str, str] | None = None,
    ) -> Iterator[Iterator[str]]:
        """Record a stream request and expose the fixed response lines.

        Yields:
            An iterator over the configured response lines.

        """
        self.requests.append((path, headers))
        yield iter(self.lines)


class ControlTransport:
    """Represent control transport."""

    def __init__(self) -> None:
        """Create empty control request records."""
        self.posts: list[TransportPost] = []
        self.timeouts: list[float | None] = []

    def get[Response](self, path: str, _adapter: TypeAdapter[Response]) -> Response:
        """Return a control session fixture.

        Returns:
            A control session fixture.

        """
        if path == SESSION_DATA_PATH:
            return _transport_response(_adapter, session_data())
        return _transport_response(_adapter, entry.EntryPageResponse(items=(), oldest_cursor=0, has_more=False))

    def post[Response](
        self,
        path: str,
        document: BaseModel,
        _adapter: TypeAdapter[Response],
        accepted_statuses: set[int],
        *,
        timeout: float | None = None,
    ) -> tuple[int, Response]:
        """Record and answer a control request.

        Returns:
            HTTP 200 and the acknowledged control response.

        Raises:
            TypeError: If the document is not a control request body.

        """
        self.posts.append((path, document, accepted_statuses))
        self.timeouts.append(timeout)
        if not isinstance(document, control_request.ControlRequestBody):
            message = "control transport requires a control request"
            raise TypeError(message)
        return 200, _transport_response(
            _adapter,
            control_outcome_response.ControlResultResponse(
                request_id=document.request_id,
                status=ControlAcknowledgement.ACKNOWLEDGED,
                reason=None,
            ),
        )


class UploadTransport:
    """Represent upload transport."""

    def __init__(self) -> None:
        """Create an empty upload request record."""
        self.posts: list[TransportPost] = []

    def post[Response](
        self,
        path: str,
        document: BaseModel,
        _adapter: TypeAdapter[Response],
        accepted_statuses: set[int],
    ) -> tuple[int, Response]:
        """Record and answer an upload request.

        Returns:
            HTTP 200 and the fixed text upload response.

        """
        self.posts.append((path, document, accepted_statuses))
        return 200, _adapter.validate_python(
            {
                "ok": True,
                "path": "/test-data/upload-context.txt",
                "name": "context.txt",
                "mime": PLAIN_TEXT_MEDIA_TYPE,
                "is_image": False,
            },
        )
