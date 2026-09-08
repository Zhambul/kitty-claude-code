# Copyright (c) 2026 Zhambyl Yermagambet
"""Test sessiondata api session resume."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

import pytest

from tests import (
    canonical_sessiondata_api_frame_parsing as frame_parsing,
    canonical_sessiondata_api_session_reads as stream_reads,
    canonical_sessiondata_api_store as store_support,
    canonical_sessiondata_api_updates as api_updates,
    canonical_sessiondata_api_values as api_values,
)

if TYPE_CHECKING:

    from repository.impl.sqlite.session_data import SqliteSessionDataRepository


@pytest.mark.usefixtures("tmp_path")
def test_stream_resumes_from_id_client_last_saw(
    session_data_store: SqliteSessionDataRepository,
) -> None:
    """Verify a stream resumes from the id the client last saw.

    The frame id is a database cursor, not a sequence number the server
        invents — so whatever the client last saw, the next poll returns exactly
        what committed after it, across a reconnect or a daemon restart.
    """
    read_model = session_data_store
    api_updates.apply_snapshot(read_model, 1)
    api_updates.apply_prompt(
        read_model,
        2,
        entry_id_text="event-1",
        text="first",
    )
    boundary = store_support.stored_data(read_model).cursor
    api_updates.apply_prompt(
        read_model,
        3,
        message_id_text="m2",
        entry_id_text="event-2",
        text="second",
    )

    resumed = frame_parsing.frame_body(asyncio.run(stream_reads.read_reconnected_frame(read_model, boundary)))
    assert [wire_entry["entry_id"] for wire_entry in resumed[api_values.ENTRIES_FIELD]] == ["event-2"]


@pytest.mark.usefixtures("tmp_path")
def test_aggregate_only_change_advances_cursor_it(
    session_data_store: SqliteSessionDataRepository,
) -> None:
    """Verify an aggregate only change advances the cursor it was sent with.

    Otherwise the same row comes back every quarter second for the life of
        the connection: an actor row's revision is a column, not something the actor
        object carries, so the frame id has to come from the read that found it.
    """
    read_model = session_data_store
    api_updates.apply_snapshot(read_model, 1)

    first = asyncio.run(stream_reads.read_first_frame_and_confirm_no_update(read_model))
    assert frame_parsing.frame_body(first)[api_values.ACTORS_FIELD] != []
