# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the resumable session response module."""

# One session the picker can resume into.
from pydantic import BaseModel

from api.common.models.values.account_reference import AccountReferenceResponse
from api.common.models.values.model_reference import ModelReferenceResponse
from domain.ids import SessionId


class ResumableSessionResponse(BaseModel):
    """Represent resumable session response."""

    session_id: SessionId
    title: str | None
    last_activity_at: float
    active: bool
    harness: str
    model: ModelReferenceResponse | None
    effort: str | None
    account: AccountReferenceResponse | None
