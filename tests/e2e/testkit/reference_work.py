# Copyright (c) 2026 Zhambyl Yermagambet
"""Define E2E references for work and workers."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from api.controls.models.attachment_reference import AttachmentReferenceBody
from sdk.client import ActionReceipt, SessionRef
from tests.e2e.testkit.reference_continuity import TurnRef


@dataclass(frozen=True)
class AttachmentBundleRef:
    """Represent staged attachment references."""

    attachments: tuple[AttachmentReferenceBody, ...]


@dataclass(frozen=True)
class ActorRef:
    """Represent one session actor."""

    session: SessionRef
    actor_id: str


@dataclass(frozen=True)
class AssignmentRef:
    """Represent one worker assignment."""

    session: SessionRef
    assignment_id: str


class WorkerKind(StrEnum):
    """Identify a lead or subagent worker."""

    LEAD = "lead"
    SUBAGENT = "subagent"


@dataclass(frozen=True)
class WorkerRef:
    """Represent a worker in one session."""

    session: SessionRef
    kind: WorkerKind
    actor_id: str
    address: str | None = None
    parent_actor_id: str | None = None


@dataclass(frozen=True)
class WorkRef:
    """Represent one requested unit of work."""

    session: SessionRef
    requested_prompt: str
    request_turn: TurnRef
    worker: WorkerRef
    turn: TurnRef
    assignment: AssignmentRef | None = None


@dataclass(frozen=True)
class WorkerControlRef:
    """Represent a control action for one worker."""

    work: WorkRef
    receipt: ActionReceipt | None = None
    turn: TurnRef | None = None
