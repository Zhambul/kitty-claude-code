# Copyright (c) 2026 Zhambyl Yermagambet
"""Control effect close session."""

from __future__ import annotations

from typing import TYPE_CHECKING

from domain import (
    event_base,
    ids as domain_ids,
)
from engine.interpret import translators as interpret_translators
from tests import (
    control_effect_sessions as control_sessions,
    control_effect_stores as stores,
    control_effect_values as control_values,
)

if TYPE_CHECKING:
    from harness.models.session import (
        Session,
    )


def closing_session() -> Session:
    """Build the session for a close request.

    Returns:
        The Codex session with the test lead actor.

    """
    return control_sessions.codex_session(
        domain_ids.ActorId(control_values.TEST_LEAD_ACTOR_ID_TEXT),
    )


def translated_control_events(raw_events: stores.RawEvents) -> list[event_base.CanonicalEvent]:
    """Translate recorded control effects into canonical events.

    Returns:
        The first canonical event from each recorded control effect.

    """
    return [
        interpret_translators.ControlTranslator().translate(raw_event).canonical_events[0]
        for raw_event in raw_events.events
    ]
