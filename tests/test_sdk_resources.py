# Copyright (c) 2026 Zhambyl Yermagambet
"""Verify the typed SDK client."""

from __future__ import annotations

from http import HTTPStatus

import pytest
from pydantic import BaseModel, TypeAdapter

from api.controls.models.launch_session_request import LaunchSessionRequest
from api.sessiondata.models.session_data import SessionDataListResponse
from sdk import client as sdk_client
from sdk.client import (
    LAUNCH_TIMEOUT_SECONDS,
)
from tests.sdk_test_resources import sessions_resource
from tests.sdk_test_support import _transport_response

WORKING_DIRECTORY = "/work"


SUCCEEDED_FIELD = "succeeded"


WINDOW_ID_FIELD = "window_id"


WINDOW_ID_TEXT = "window-one"


type TransportPost = tuple[str, BaseModel, set[int]]


type LaunchTransportPost = tuple[str, BaseModel, set[int], float | None]


class PaneTransport:
    """Represent pane transport."""

    def __init__(self) -> None:
        """Create an empty pane request record."""
        self.posts: list[TransportPost] = []

    def post[Response](
        self,
        path: str,
        document: BaseModel,
        adapter: TypeAdapter[Response],
        accepted_statuses: set[int],
    ) -> tuple[int, Response]:
        """Record and answer a pane request.

        Returns:
            HTTP 200 and a successful handled response.

        """
        self.posts.append((path, document, accepted_statuses))
        return 200, adapter.validate_python(
            {
                "handled": True,
                SUCCEEDED_FIELD: True,
                "reason": None,
            },
        )


class LaunchTransport:
    """Represent launch transport."""

    def __init__(self) -> None:
        """Create an empty launch request record."""
        self.posts: list[LaunchTransportPost] = []

    def get[Response](self, path: str, _adapter: TypeAdapter[Response]) -> Response:
        """Return an empty session list.

        Returns:
            An empty session list.

        """
        assert path == "/sessionData"
        return _transport_response(_adapter, SessionDataListResponse(cursor=0, sessions=()))

    def post[Response](
        self,
        path: str,
        document: BaseModel,
        adapter: TypeAdapter[Response],
        accepted_statuses: set[int],
        *,
        timeout: float | None = None,
    ) -> tuple[int, Response]:
        """Record and answer a launch request.

        Returns:
            HTTP 202 and a started response with the test window identifier.

        """
        self.posts.append((path, document, accepted_statuses, timeout))
        return 202, adapter.validate_python(
            {
                "status": "started",
                WINDOW_ID_FIELD: WINDOW_ID_TEXT,
                "reason": None,
            },
        )


def test_session_launch_sends_explicit_account() -> None:
    """Verify session launch sends an explicit account selection."""
    transport = LaunchTransport()

    sessions_resource(transport).launch(
        sdk_client.SessionLaunchRequest(
            "claude_code",
            workspace=WORKING_DIRECTORY,
            prompt="hello",
            model="haiku",
            effort="low",
            account_id="account-one",
        ),
    )

    path, document, statuses, timeout = transport.posts[0]
    assert path == "/api/sessions"
    assert isinstance(document, LaunchSessionRequest)
    assert document.account_id == "account-one"
    assert statuses == {HTTPStatus.ACCEPTED, HTTPStatus.CONFLICT}
    assert timeout == pytest.approx(LAUNCH_TIMEOUT_SECONDS)
