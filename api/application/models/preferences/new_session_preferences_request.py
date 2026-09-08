# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the new session preferences request module."""

# The remembered new-session form selections.
from pydantic import BaseModel


class NewSessionPreferencesRequest(BaseModel):
    """Represent new session preferences request."""

    working_directory: str | None = None
    harness: str | None = None
    model: str | None = None
    effort: str | None = None
