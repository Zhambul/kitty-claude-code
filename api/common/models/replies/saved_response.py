# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the saved response module."""

# The persisted-preference reply.
from pydantic import BaseModel


class SavedResponse(BaseModel):
    """Represent saved response."""

    saved: bool = True
