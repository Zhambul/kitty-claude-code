# Copyright (c) 2026 Zhambyl Yermagambet
"""Immutable values for a person's unfinished dialog input."""

from dataclasses import dataclass

from domain.ids import AttentionId


@dataclass(frozen=True)
class AnswerSelection:
    """Hold one prompt's selected choices and custom answer."""

    selected: tuple[str, ...]
    other: str


@dataclass(frozen=True)
class DialogDraft:
    """Hold unfinished answers for one attention request."""

    attention_id: AttentionId
    answers: tuple[AnswerSelection, ...]
    origin: str


@dataclass(frozen=True)
class DialogState:
    """Hold the current unfinished dialog for a session."""

    draft: DialogDraft | None
