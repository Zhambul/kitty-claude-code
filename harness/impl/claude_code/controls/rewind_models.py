# Copyright (c) 2026 Zhambyl Yermagambet
"""Store Claude Code rewind values and errors."""

from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum

from domain.ids import WindowId
from harness.impl.claude_code.controls import screen_driver, screen_protocols


class ClaudeCodeRewindMode(StrEnum):
    """Identify one native rewind mode."""

    BOTH = "both"
    CONVERSATION = "conversation"
    CODE = "code"

    @property
    def label(self) -> str:
        """The terminal label for this rewind mode."""
        if self is ClaudeCodeRewindMode.BOTH:
            return "restore code and conversation"
        if self is ClaudeCodeRewindMode.CONVERSATION:
            return "restore conversation"
        return "restore code"


@dataclass(frozen=True)
class ConfirmOption:
    """Describe one rewind confirmation option."""

    label: str
    digit: str
    cursor: bool


class MenuError(screen_driver.StepError):
    """Report a rewind menu step that did not reach its required state."""


@dataclass(frozen=True)
class RewindOutcome:
    """Report the result of a successful rewind operation."""

    steps: int
    digit: str
    degraded: bool


@dataclass(frozen=True)
class RewindRequest:
    """Describe one requested rewind operation."""

    target: str
    mode: str
    hint_steps: int = 0


@dataclass(frozen=True)
class RewindContext:
    """Provide terminal operations for one rewind flow."""

    screen_driver: screen_protocols.RewindScreenDriver
    window_id: WindowId
    sleep: Callable[[float], None]


def mode_label(mode: str) -> str | None:
    """Return the native menu label for one rewind mode.

    Returns:
        The menu label, or None for an invalid mode.

    """
    try:
        rewind_mode = ClaudeCodeRewindMode(mode)
    except ValueError:
        return None
    return rewind_mode.label
