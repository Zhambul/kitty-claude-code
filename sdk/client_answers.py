# Copyright (c) 2026 Zhambyl Yermagambet
"""Split SDK client implementation."""

from __future__ import annotations

from dataclasses import dataclass

from sdk import application_models


@dataclass(frozen=True)
class QuestionAnswer:
    """Represent question answer."""

    selected: tuple[str, ...] = ()
    other: str = ""


def _answer_selection(answer: QuestionAnswer) -> application_models.dialog_draft_request.AnswerSelectionBody:
    return application_models.dialog_draft_request.AnswerSelectionBody(selected=answer.selected, other=answer.other)
