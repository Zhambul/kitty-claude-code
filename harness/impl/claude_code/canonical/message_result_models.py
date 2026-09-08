# Copyright (c) 2026 Zhambyl Yermagambet
"""Define Claude Code result translation models."""

from __future__ import annotations

from dataclasses import dataclass

from domain import ids as domain_ids
from domain.event_base import CanonicalEvent, EventPayload


@dataclass(frozen=True)
class LoadedSkills:
    """Keep skill events and the text block indexes used to produce them."""

    events: list[CanonicalEvent[EventPayload]]
    text_indexes: set[int]


@dataclass(frozen=True)
class ResultInterruption:
    """Track a result's interrupted turn and prior abort emission."""

    turn_id: domain_ids.TurnId | None
    abort_already_emitted: bool


@dataclass(frozen=True)
class ResultPrompt:
    """Keep result prompt events and their turn identifier."""

    events: list[CanonicalEvent[EventPayload]]
    turn_id: domain_ids.TurnId | None
