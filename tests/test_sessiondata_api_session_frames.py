# Copyright (c) 2026 Zhambyl Yermagambet
"""Test sessiondata api session frames."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

import pytest

from repository.contract import session_data as session_data_contract
from tests import (
    canonical_sessiondata_api_change_reads as change_reads,
    canonical_sessiondata_api_frame_parsing as frame_parsing,
    canonical_sessiondata_api_session_reads as stream_reads,
    canonical_sessiondata_api_values as api_values,
)

if TYPE_CHECKING:

    from repository.impl.sqlite.session_data import SqliteSessionDataRepository


@pytest.mark.usefixtures("tmp_path")
def test_session_stream_frame_per_change(
    session_data_store: SqliteSessionDataRepository,
) -> None:
    """Verify a session stream sends a frame after a change notice."""
    read_model = session_data_store
    read_model.apply(
        api_values.SESSION,
        session_data_contract.SessionDataChanges(session=api_values.FACTS, actors=api_values.ACTOR_ROWS),
        1,
    )

    first, second = asyncio.run(change_reads.read_two_session_frames(read_model))

    opening = frame_parsing.frame_body(first)
    assert (
        opening["session"]["title"],
        [row["status"] for row in opening[api_values.ACTORS_FIELD]],
        opening[api_values.ENTRIES_FIELD],
    ) == (api_values.SESSION_TITLE, ["executing"], [])

    news = frame_parsing.frame_body(second)
    # Only what changed: the session part is absent, the actor is the new one,
    # and the entry rides the same frame as the status it implies.
    assert news["session"] is None
    assert [row["status"] for row in news[api_values.ACTORS_FIELD]] == ["thinking"]
    assert [wire_entry["type"] for wire_entry in news[api_values.ENTRIES_FIELD]] == ["message"]
    assert frame_parsing.frame_id(second) > frame_parsing.frame_id(first)


@pytest.mark.usefixtures("tmp_path")
def test_session_stream_starts_with_shared_app(session_data_store: SqliteSessionDataRepository) -> None:
    """Verify a session stream starts with the shared application state."""
    read_model = session_data_store
    read_model.apply(
        api_values.SESSION,
        session_data_contract.SessionDataChanges(session=api_values.FACTS, actors=api_values.ACTOR_ROWS),
        1,
    )

    application, session_data = asyncio.run(stream_reads.read_application_and_session_frames(read_model))

    assert "event: application" in application
    assert "id:" not in application
    assert frame_parsing.frame_body(application)["composer"]["draft"]["text"] == "test"
    assert "event: sessionData" in session_data
