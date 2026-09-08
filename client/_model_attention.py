# Copyright (c) 2026 Zhambyl Yermagambet
"""Model attention."""

from __future__ import annotations

from _model_base import WireModel


class QuestionChoiceRecord(WireModel):
    label: str
    description: str | None = None


class QuestionRecord(WireModel):
    title: str | None = None
    question: str = ""
    multiple: bool = False
    choices: tuple[QuestionChoiceRecord, ...] = ()


class AnswerRecord(WireModel):
    labels: tuple[str, ...] = ()
