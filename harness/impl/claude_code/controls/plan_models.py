# Copyright (c) 2026 Zhambyl Yermagambet
"""Store Claude Code plan dialog values and errors."""

from dataclasses import dataclass

from harness.impl.claude_code.controls import screen_driver


@dataclass(frozen=True)
class Option:
    """Describe one plan decision option."""

    digit: str
    label: str
    feedback: bool


@dataclass(frozen=True)
class Decided:
    """Report the selected plan decision."""

    decided: str


@dataclass(frozen=True)
class Fedback:
    """Report that the user sent plan feedback."""

    feedback: bool


@dataclass(frozen=True)
class Dismissed:
    """Report that the user dismissed the plan."""

    dismissed: bool


class PlanError(screen_driver.StepError):
    """Report a plan dialog step that did not reach its required state."""
