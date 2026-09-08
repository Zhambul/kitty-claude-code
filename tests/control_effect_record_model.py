# Copyright (c) 2026 Zhambyl Yermagambet
"""Control effect record model."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from engine.interpret import translators as interpret_translators
from harness.models.session import (
    Session,
)
from harness.services.control_effects import ControlEffectRecorder
from tests import control_effect_stores as stores

if TYPE_CHECKING:
    from domain import (
        event_base,
    )


@dataclass(frozen=True)
class ControlEffectFixture:
    """Hold a control recorder, its source events, and its session."""

    raw_events: stores.RawEvents
    recorder: ControlEffectRecorder
    session: Session

    def translated_event(self) -> event_base.CanonicalEvent:
        """Translate the single required control effect.

        Returns:
            The single canonical event from the recorded effect.

        """
        assert len(self.raw_events.events) == 1
        translation = interpret_translators.ControlTranslator().translate(
            self.raw_events.events[0],
        )
        assert len(translation.canonical_events) == 1
        return translation.canonical_events[0]
