# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the model reference module."""

# Which model a session, an actor or a change is talking about.
from pydantic import BaseModel


class ModelReferenceResponse(BaseModel):
    """Represent model reference response."""

    name: str
    display_name: str | None
