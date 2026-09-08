# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the global notifications request module."""

# The global notification switch.
from pydantic import BaseModel


class GlobalNotificationsRequest(BaseModel):
    """Represent global notifications request."""

    enabled: bool
