# Copyright (c) 2026 Zhambyl Yermagambet
"""Define skill entry bodies."""

from __future__ import annotations

from pydantic import BaseModel

from api.common.models.values.content import ContentResponse
from domain.entry_base import RunState


class SkillStartedBodyResponse(BaseModel):
    """Represent a skill-started entry body."""

    skill_id: str
    name: str
    arguments: ContentResponse | None


class SkillFinishedBodyResponse(BaseModel):
    """Represent a skill-finished entry body."""

    skill_id: str
    state: RunState
    result: ContentResponse | None
