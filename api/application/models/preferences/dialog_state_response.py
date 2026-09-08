# Copyright (c) 2026 Zhambyl Yermagambet
"""Define the session dialog response."""

from pydantic import BaseModel

from domain.ids import AttentionId


class AnswerSelectionResponse(BaseModel):
    """Represent an answer selection response."""

    selected: tuple[str, ...]
    other: str


class DialogDraftResponse(BaseModel):
    """Represent a dialog draft response."""

    attention_id: AttentionId
    answers: tuple[AnswerSelectionResponse, ...]
    origin: str


class DialogStateResponse(BaseModel):
    """Represent a dialog state response."""

    draft: DialogDraftResponse | None
