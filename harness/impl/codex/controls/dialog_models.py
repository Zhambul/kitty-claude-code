# Copyright (c) 2026 Zhambyl Yermagambet
"""Define Codex question-dialog data."""

from dataclasses import dataclass
from enum import StrEnum


@dataclass(frozen=True)
class PromptChoice:
    """Represent one prompt choice."""

    label: str
    description: str


@dataclass(frozen=True)
class Prompt:
    """Represent one pending prompt."""

    id: str = ""
    header: str = ""
    question: str = ""
    options: tuple[PromptChoice, ...] = ()


@dataclass(frozen=True)
class OptionRow:
    """Represent one visible option row."""

    num: str
    label: str
    cursor: bool


@dataclass(frozen=True)
class Answer:
    """Represent one prompt answer."""

    selected: tuple[str, ...] = ()
    other: str = ""


@dataclass(frozen=True)
class QuestionSet:
    """Pair pending prompts with answers."""

    questions: list[Prompt]
    answers: list[Answer]


class DialogOutcome(StrEnum):
    """Represent a dialog result."""

    SUBMITTED = "submitted"


class CodexAskError(Exception):
    """Report a failed Codex question-dialog action."""

    def __init__(self, step: str, detail: str = "") -> None:
        """Initialize the object."""
        super().__init__(f"{step}: {detail}" if detail else step)
        self.step = step
        self.detail = detail
