# Copyright (c) 2026 Zhambyl Yermagambet
"""Canonical payloads for actor lifecycle and assignment changes."""

from dataclasses import dataclass

from domain.content import Content
from domain.event_base import EventPayload
from domain.ids import AssignmentId
from domain.messaging import ActorRole
from domain.outcomes import Outcome


@dataclass(frozen=True)
class ActorStarted(EventPayload):
    """Record the start of one actor."""

    name: str
    role: ActorRole


@dataclass(frozen=True)
class ActorNameChanged(EventPayload):
    """Record a new actor display name."""

    name: str


@dataclass(frozen=True)
class ActorDescriptionChanged(EventPayload):
    """Record a new actor description."""

    description: str


@dataclass(frozen=True)
class ActorFinished(EventPayload):
    """Record the end of one actor."""

    reason: str | None


@dataclass(frozen=True)
class ActorAssignmentStarted(EventPayload):
    """Record the start of a child-agent assignment."""

    assignment_id: AssignmentId
    brief: Content
    actor_name: str | None = None
    prompt: Content | None = None


@dataclass(frozen=True)
class ActorAssignmentFinished(EventPayload):
    """Record the final outcome of a child-agent assignment."""

    assignment_id: AssignmentId
    outcome: Outcome
    result: Content | None
    reason: str | None
