# Copyright (c) 2026 Zhambyl Yermagambet
"""Confirmed observations from harness control commands."""

from dataclasses import dataclass

from domain.ids import AssignmentId, AttentionId, RequestId, ShellId, TurnId
from domain.outcomes import PlanState
from domain.stored import STORED
from domain.work_state import OpenWorkKind, TitleOrigin


@dataclass(frozen=True)
class PlanDecisionObservation:
    """Record a plan decision that the control driver confirmed."""

    __pydantic_config__ = STORED

    attention_id: AttentionId
    state: PlanState
    feedback: str | None
    edited: bool
    turn_id: TurnId | None


@dataclass(frozen=True)
class MessageQueueObservation:
    """Record a message that a harness confirmed in its queue."""

    __pydantic_config__ = STORED

    request_id: RequestId
    text: str


@dataclass(frozen=True)
class SessionRenameObservation:
    """Record a confirmed write to a parked harness title store."""

    __pydantic_config__ = STORED

    title: str
    origin: TitleOrigin


@dataclass(frozen=True)
class ModelSelectionObservation:
    """Record a model selection confirmed by a control driver."""

    __pydantic_config__ = STORED

    model: str


@dataclass(frozen=True)
class EffortSelectionObservation:
    """Record an effort selection confirmed by a control driver."""

    __pydantic_config__ = STORED

    effort: str


@dataclass(frozen=True)
class SessionCloseWorkObservation:
    """Record one open work item at the session-close boundary."""

    __pydantic_config__ = STORED

    kind: OpenWorkKind
    subject_id: TurnId | ShellId | AssignmentId
    turn_id: TurnId | None
