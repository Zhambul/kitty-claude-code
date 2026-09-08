# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the presence request module."""

# One device's presence beat.
from pydantic import BaseModel

from api.common.models.fields import RequiredText


class PresenceRequest(BaseModel):
    """Represent presence request."""

    device_id: RequiredText
    session_id: str | None = None
    away: bool = False
