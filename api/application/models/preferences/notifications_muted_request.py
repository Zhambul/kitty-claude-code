# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the notifications muted request module."""

# One session's notification mute switch.
from pydantic import BaseModel


class NotificationsMutedRequest(BaseModel):
    """Represent notifications muted request."""

    muted: bool
