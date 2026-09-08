# Copyright (c) 2026 Zhambyl Yermagambet
"""Test sessiondata api global stream."""

from __future__ import annotations

import asyncio
from dataclasses import replace
from typing import TYPE_CHECKING

import pytest

from domain import ids as domain_ids
from repository.contract import session_data as session_data_contract
from tests import (
    canonical_sessiondata_api_frame_parsing as frame_parsing,
    canonical_sessiondata_api_global_stream_reads as global_stream_reads,
    canonical_sessiondata_api_updates as api_updates,
    canonical_sessiondata_api_values as api_values,
)

if TYPE_CHECKING:

    from repository.impl.sqlite.session_data import SqliteSessionDataRepository


@pytest.mark.usefixtures("tmp_path")
def test_global_stream_carries_every_session(session_data_store: SqliteSessionDataRepository) -> None:
    """It drives the list and the tab colours, and neither reads an entry."""
    read_model = session_data_store
    other = domain_ids.SessionId("session-two")
    read_model.apply(
        api_values.SESSION,
        session_data_contract.SessionDataChanges(session=api_values.FACTS, actors=api_values.ACTOR_ROWS),
        1,
    )
    read_model.apply(
        other,
        session_data_contract.SessionDataChanges(
            session=replace(api_values.FACTS, session_id=other, title="Another"),
            actors=(replace(api_values.ACTOR, session_id=other),),
        ),
        2,
    )
    api_updates.apply_prompt(read_model, 3)

    ready, application_frame, frame = asyncio.run(global_stream_reads.read_global_frames(read_model))
    frame_parsing.assert_ready_frame(ready)
    assert (
        "event: application" in application_frame,
        "id:" not in application_frame,
        frame_parsing.frame_body(application_frame)["notifications"]["enabled"],
    ) == (True, True, True)
    assert (
        {row["session_id"] for row in frame_parsing.frame_body(frame)["sessions"]},
        len(frame_parsing.frame_body(frame)[api_values.ACTORS_FIELD]),
        api_values.ENTRIES_FIELD not in frame_parsing.frame_body(frame),
    ) == ({api_values.SESSION_ID_TEXT, "session-two"}, 2, True)
