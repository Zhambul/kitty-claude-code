# Copyright (c) 2026 Zhambyl Yermagambet
"""Own plan arguments models."""

from __future__ import annotations

from collections.abc import Mapping

from pydantic import BaseModel, RootModel

from harness.impl.codex.canonical.record_config import FOREIGN
from harness.impl.codex.canonical.record_execution_arguments import AskAnswer


class AskAnswers(RootModel[Mapping[str, AskAnswer]]):
    """Represent ask answers."""


class AskResultDocument(BaseModel):
    """The value Codex records for a completed request_user_input call."""

    model_config = FOREIGN
    answers: AskAnswers


class PlanTask(BaseModel):
    """Represent plan task."""

    model_config = FOREIGN
    step: str | None = None
    status: str | None = None


class PlanArguments(BaseModel):
    """Represent plan arguments."""

    model_config = FOREIGN
    plan: list[PlanTask] | None = None


class GoalArguments(BaseModel):
    """Represent goal arguments."""

    model_config = FOREIGN
    objective: str | None = None
    status: str | None = None
    reason: str | None = None
    token_budget: int | None = None
