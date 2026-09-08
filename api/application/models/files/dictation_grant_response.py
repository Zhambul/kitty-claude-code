# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the dictation grant response module."""

# The short-lived grant plus the assembled listen URL.
from pydantic import BaseModel


class DictationGrantResponse(BaseModel):
    """Represent dictation grant response."""

    token: str
    expires_in: int | None
    ws_url: str
