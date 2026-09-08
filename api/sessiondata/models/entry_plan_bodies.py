# Copyright (c) 2026 Zhambyl Yermagambet
"""Define plan entry bodies."""

from __future__ import annotations

from pydantic import BaseModel

from api.common.models.values.content import ContentResponse
from domain.outcomes import PlanState


class PlanProposedBodyResponse(BaseModel):
    """Represent a plan-proposed entry body."""

    attention_id: str
    plan: ContentResponse


class PlanResolvedBodyResponse(BaseModel):
    """Represent a plan-resolved entry body."""

    attention_id: str
    state: PlanState
    feedback: str | None
    edited: bool
