# Copyright (c) 2026 Zhambyl Yermagambet
"""Canonical payloads for session and selection lifecycle changes."""

from dataclasses import dataclass

from domain.event_base import EventPayload
from domain.ids import SessionId
from domain.outcomes import Outcome
from domain.references import AccountReference, ModelReference
from domain.work_state import EffortChangeReason, ModelChangeReason, TitleOrigin


@dataclass(frozen=True)
class SessionStarted(EventPayload):
    """Record the start or resume of one harness session."""

    working_directory: str
    source_reference: str
    resumed_from: SessionId | None
    title: str | None
    model: ModelReference | None
    effort: str | None
    account: AccountReference | None
    continued_from: SessionId | None = None


@dataclass(frozen=True)
class SessionTitleChanged(EventPayload):
    """Record a new session title and its source."""

    title: str
    origin: TitleOrigin


@dataclass(frozen=True)
class SessionAccountChanged(EventPayload):
    """Record the account that a session now uses."""

    account: AccountReference


@dataclass(frozen=True)
class SessionFinished(EventPayload):
    """Record the final outcome of a session."""

    outcome: Outcome
    reason: str | None


@dataclass(frozen=True)
class ModelChanged(EventPayload):
    """Record a model change and its cause."""

    previous: ModelReference | None
    current: ModelReference
    reason: ModelChangeReason


@dataclass(frozen=True)
class EffortChanged(EventPayload):
    """Record an effort change and its cause."""

    previous: str | None
    current: str
    reason: EffortChangeReason
