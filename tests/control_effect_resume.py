# Copyright (c) 2026 Zhambyl Yermagambet
"""Record a resumed session for control effect tests."""

from typing import TYPE_CHECKING, cast

from domain import ids as domain_ids
from harness.models.session import Session
from harness.services.launch_effects import SessionLaunchEffectRecorder
from tests import control_effect_stores as stores, control_effect_values as control_values

if TYPE_CHECKING:
    from repository.contract.facts import RawEventRepository
    from repository.contract.sessions import SessionRepository


def resumed_raw_events(
    harness_name: domain_ids.HarnessName,
    source_name: str,
    window_id: domain_ids.WindowId,
) -> stores.RawEvents:
    """Record one resumed session.

    Returns:
        The raw-event recorder containing the resume events.

    """
    raw_events = stores.RawEvents()
    session = Session(
        control_values.TEST_SESSION_ID,
        control_values.TEST_ACTOR_ID,
        source_name,
        control_values.TEST_WORKING_DIRECTORY,
    )
    recorder = SessionLaunchEffectRecorder(
        cast("RawEventRepository", raw_events),
        cast("SessionRepository", stores.Sessions(session)),
    )
    recorder.resumed(harness_name, session.session_id, window_id)
    return raw_events
