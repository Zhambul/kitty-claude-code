# Copyright (c) 2026 Zhambyl Yermagambet
"""Test control effect titles."""

from __future__ import annotations

from domain import (
    event_session,
    work_state,
)
from harness.models import controls as control_models
from tests import control_effect_recording as recording, control_effect_values as control_values


def test_confirmed_parked_rename_becomes_one() -> None:
    """Verify confirmed parked rename becomes one canonical title change."""
    control_fixture = recording.control_effect_fixture()
    request = control_models.RenameSession(
        control_fixture.session.session_id,
        control_values.TEST_REQUEST_ID,
        "Parked title",
    )

    control_fixture.recorder.session_renamed(control_fixture.session, request)

    assert control_fixture.raw_events.events[0].source_name == "session_rename"
    event = control_fixture.translated_event()
    assert event.actor_id == control_values.TEST_ACTOR_ID
    assert event.turn_id is None
    assert event.payload == event_session.SessionTitleChanged(
        "Parked title",
        work_state.TitleOrigin.CUSTOM,
    )
