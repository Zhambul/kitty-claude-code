# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the dictation token request module."""

# The browser's dictation-grant request.
from pydantic import BaseModel

from api.common.models.fields import RequiredText


class DictationTokenRequest(BaseModel):
    """Represent dictation token request."""

    sample_rate: int
    harness: RequiredText
    working_directory: str | None = None
