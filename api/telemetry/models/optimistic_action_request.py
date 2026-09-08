# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the optimistic action request module."""

# One optimistic-UI lifecycle report.
from enum import StrEnum

from pydantic import BaseModel


class OptimisticActionKind(StrEnum):
    """Represent optimistic action kind."""

    COMPOSER = "composer"
    CLOSE = "close"
    ANSWER = "answer"
    PLAN = "plan"


class OptimisticActionPhase(StrEnum):
    """Represent optimistic action phase."""

    SHOWN = "shown"
    RECONCILED = "reconciled"
    DROPPED = "dropped"
    STALE = "stale"


class OptimisticActionRequest(BaseModel):
    """Represent optimistic action request."""

    action: OptimisticActionKind
    phase: OptimisticActionPhase
    character_count: int | None = None
    elapsed_milliseconds: int | None = None
    reason: str | None = None
