# Copyright (c) 2026 Zhambyl Yermagambet
"""Verify the typed SDK client."""

from __future__ import annotations

from typing import cast

import pytest

from sdk.client import (
    SessionRef,
    SessionWatch,
    StreamsResource,
)
from sdk.state import SessionSnapshot
from sdk.transport import ApiFailureError, HttpTransport
from tests.e2e.testkit import selector_shells, selector_turns
from tests.e2e.testkit.references import TurnRef
from tests.sdk_test_resources import streams_resource
from tests.sdk_test_support import (
    message_entry,
    prompt_entry,
    session_data,
    shell_entry,
)
from tests.sdk_test_transports import (
    EventStreamTransport,
    FixedWatch,
)
from tests.test_sdk_snapshots import PromptOwnerSessions

INITIAL_CURSOR = 1_001
SESSION_UPDATE_CURSOR = 7
GLOBAL_UPDATE_CURSOR = 8


NEXT_CURSOR = 1_002


SESSION_ID_TEXT = "session-one"


SESSION = SessionRef(SESSION_ID_TEXT)


FIRST_TURN_ID = "turn-one"


OLD_SESSION_ID = "session-old"


def test_session_stream_returns_typed_update() -> None:
    """Verify the session stream returns a typed update and sends the resume cursor."""
    entry_document = message_entry(SESSION_UPDATE_CURSOR).model_dump_json()
    transport = EventStreamTransport(
        [
            ": heartbeat",
            "event: sessionData",
            f"id: {SESSION_UPDATE_CURSOR}",
            f'data: {{"entries":[{entry_document}]}}',
            "",
        ],
    )
    streams = streams_resource(transport)

    update = streams.next_session_update(
        SESSION,
        after_cursor=2,
        last_event_id=5,
    )

    assert update.cursor == SESSION_UPDATE_CURSOR
    assert [entry.entry_id for entry in update.frame.entries] == ["entry-7"]
    assert transport.requests == [
        (
            "/sessionData/session-one/stream?after_cursor=2",
            {"Last-Event-ID": "5"},
        ),
    ]


def test_global_stream_skips_ready_and_returns() -> None:
    """Verify the global stream skips ready and returns a typed update."""
    session_document = session_data(GLOBAL_UPDATE_CURSOR).session.model_dump_json()
    transport = EventStreamTransport(
        [
            "event: ready",
            'data: {"boot_id":"boot-one"}',
            "",
            "event: sessionData",
            f"id: {GLOBAL_UPDATE_CURSOR}",
            f'data: {{"sessions":[{session_document}]}}',
            "",
        ],
    )
    streams = streams_resource(transport)

    update = streams.next_global_update(after_cursor=3)

    assert update.cursor == GLOBAL_UPDATE_CURSOR
    assert [session.session_id for session in update.frame.sessions] == [SESSION_ID_TEXT]
    assert transport.requests == [("/sessionData/stream?after_cursor=3", None)]


def test_stream_error_frame_becomes_api_failure() -> None:
    """Verify a stream error frame becomes an API failure."""
    streams = StreamsResource(
        cast(
            "HttpTransport",
            EventStreamTransport(
                [
                    "event: error",
                    'data: {"error":"stream failed"}',
                    "",
                ],
            ),
        ),
    )

    with pytest.raises(ApiFailureError, match="stream failed"):
        streams.next_global_update(after_cursor=0)


def test_prompt_owner_follows_declared_session() -> None:
    """Verify prompt owner follows a declared session continuation."""
    source = SessionSnapshot(
        session_data(session_id=OLD_SESSION_ID, live=False),
        (),
    )
    continuation = SessionSnapshot(
        session_data(
            cursor=NEXT_CURSOR,
            session_id="session-new",
            continued_from=OLD_SESSION_ID,
        ),
        (prompt_entry(NEXT_CURSOR, "Revised prompt"),),
    )
    sessions = PromptOwnerSessions(
        {
            OLD_SESSION_ID: source,
            "session-new": continuation,
        },
    )

    owner = sessions.wait_for_prompt_owner(
        SessionRef(OLD_SESSION_ID),
        prompt="Revised prompt",
        after_cursor=INITIAL_CURSOR,
        timeout=0.1,
    )

    assert owner == SessionRef("session-new")


def test_a_selector_rejects_two_matching_commands() -> None:
    """Verify a selector rejects two matching commands."""
    snapshot = SessionSnapshot(
        session_data=session_data(3),
        entries=(shell_entry(1, "shell-one"), shell_entry(2, "shell-two")),
    )

    with pytest.raises(AssertionError, match="matched 2 objects"):
        selector_shells.shell(
            cast("SessionWatch", FixedWatch(snapshot)),
            selector_shells.ShellCriteria(command_contains="echo duplicate"),
            timeout=1.0,
        )


def test_launch_turn_uses_prompt_that_harness() -> None:
    """Verify a launch turn uses the prompt that the harness delivered."""
    delivered = "/test-data/context.txt\nRead the attachment."
    snapshot = SessionSnapshot(session_data(1), (prompt_entry(1, delivered),))

    found = selector_turns.launched_turn(cast("SessionWatch", FixedWatch(snapshot)), timeout=1.0)

    assert found.prompt == delivered
    assert found.turn_id == FIRST_TURN_ID
    assert found.prompt_cursor == 1


def test_turn_matches_named_native_attachment() -> None:
    """Verify a turn matches a named native attachment and the exact prompt suffix."""
    reference = TurnRef(
        SESSION,
        "Inspect the image. Reply only with its code.",
        0,
        1,
        native_attachment_names=("visible-marker.png",),
    )

    assert selector_turns.prompt_matches(
        reference,
        '[Image #1]Image attachment "visible-marker.png":\nInspect the image. Reply only with its code.',
    )
    assert not selector_turns.prompt_matches(
        reference,
        '[Image #1]Image attachment "other.png":\nInspect the image. Reply only with its code.',
    )
    assert not selector_turns.prompt_matches(
        reference,
        '[Image #1]Image attachment "visible-marker.png":\nInspect a different image.',
    )
