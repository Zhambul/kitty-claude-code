# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the composer draft request module."""

# The composer's unsent text (sequence resolves write races).
from pydantic import BaseModel


class ComposerDraftRequest(BaseModel):
    """Represent composer draft request."""

    text: str
    origin: str
    sequence: float
