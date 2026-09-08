# Copyright (c) 2026 Zhambyl Yermagambet
"""Define compaction, assignment, and setting entry bodies."""

from __future__ import annotations

from pydantic import BaseModel

from api.common.models.values.content import ContentResponse
from domain.entry_base import RunState


class CompactionStartedBodyResponse(BaseModel):
    """Represent a compaction-started entry body."""

    before_tokens: int | None


class CompactionFinishedBodyResponse(BaseModel):
    """Represent a compaction-finished entry body."""

    before_tokens: int | None
    after_tokens: int | None
    context: ContentResponse | None


class AssignmentStartedBodyResponse(BaseModel):
    """Represent an assignment-started entry body."""

    assignment_id: str
    assigned_actor_name: str | None
    prompt: ContentResponse | None


class AssignmentFinishedBodyResponse(BaseModel):
    """Represent an assignment-finished entry body."""

    assignment_id: str
    state: RunState
    result: ContentResponse | None


class ModelChangeBodyResponse(BaseModel):
    """Represent a model-change entry body."""

    current: str
    previous: str | None
    automatic: bool


class EffortChangeBodyResponse(BaseModel):
    """Represent an effort-change entry body."""

    current: str
    previous: str | None
