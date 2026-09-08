# Copyright (c) 2026 Zhambyl Yermagambet
"""Define live plan dialog choice results."""

from __future__ import annotations

from dataclasses import dataclass

from harness.models.control_outcomes import ControlResult


@dataclass(frozen=True)
class PlanChoice:
    """Represent one plan dialog choice."""

    digit: str
    label: str
    feedback: bool = False


@dataclass(frozen=True)
class PlanChoicesResult(ControlResult):
    """Represent a plan choices result."""

    choices: tuple[PlanChoice, ...] = ()
