# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the dialog draft request module."""

# The unsubmitted answers of one attention dialog.
from pydantic import BaseModel

from api.common.models.fields import RequiredText


class AnswerSelectionBody(BaseModel):
    """Represent answer selection body."""

    selected: tuple[str, ...]
    other: str


class DialogDraftRequest(BaseModel):
    """Represent dialog draft request."""

    attention_id: RequiredText
    origin: str
    answers: tuple[AnswerSelectionBody, ...]
