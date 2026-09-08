# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the new session draft request module."""

# One per-directory new-session draft (sequence resolves write races).
from pydantic import BaseModel


class NewSessionDraftRequest(BaseModel):
    """Represent new session draft request."""

    working_directory: str = ""
    text: str
    sequence: float
