# Copyright (c) 2026 Zhambyl Yermagambet
"""Build the common control effect recorder fixture."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from harness.services.control_effects import ControlEffectRecorder
from tests import (
    control_effect_record_model as record_model,
    control_effect_sessions as control_sessions,
    control_effect_stores as stores,
)

if TYPE_CHECKING:
    from domain import entries as domain_entries
    from harness.models.session import Session
    from repository.contract.facts import RawEventRepository
    from repository.contract.session_data import SessionDataRepository


def control_effect_fixture(
    entries: tuple[domain_entries.SessionEntry, ...] = (),
    session: Session | None = None,
) -> record_model.ControlEffectFixture:
    """Build a control effect recorder with in-memory test stores.

    Returns:
        The source event store, recorder, and selected session.

    """
    raw_events = stores.RawEvents()
    return record_model.ControlEffectFixture(
        raw_events,
        ControlEffectRecorder(
            cast("RawEventRepository", raw_events),
            cast("SessionDataRepository", stores.SessionEntries(entries)),
        ),
        session or control_sessions.codex_session(),
    )
