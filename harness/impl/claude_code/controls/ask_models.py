# Copyright (c) 2026 Zhambyl Yermagambet
"""Store Claude Code question dialog values."""

from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum

from pydantic import BaseModel, ConfigDict

from domain.ids import WindowId
from harness.impl.claude_code.canonical.records import Question
from harness.impl.claude_code.controls import screen_driver, screen_protocols


class AnswerDraft(BaseModel):
    """Describe one answer from the web client."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    selected: list[str] | None = None
    other: str | None = None


@dataclass(frozen=True)
class AskRequest:
    """Describe one requested question dialog action."""

    questions: list[Question]
    answers: list[AnswerDraft]
    chat: bool = False


class AskError(screen_driver.StepError):
    """Report a question dialog step that did not reach its required state."""


class AskOutcome(StrEnum):
    """Identify one completed question dialog outcome."""

    SUBMITTED = "submitted"
    CHAT = "chat"


@dataclass(frozen=True)
class NavigationContext:
    """Provide screen operations for question dialog navigation."""

    screen_driver: screen_protocols.ScreenDriver
    window_id: WindowId
    sleep: Callable[[float], None]


@dataclass(frozen=True)
class AskContext(NavigationContext):
    """Provide the state and operations for one question dialog flow."""

    screen_driver: screen_protocols.PasteScreenDriver
    questions: list[Question]
