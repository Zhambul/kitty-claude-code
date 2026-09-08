# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the push configuration response module."""

# The Web Push feature probe's answer.
from pydantic import BaseModel


class PushConfigurationResponse(BaseModel):
    """Represent push configuration response."""

    enabled: bool
    key: str | None
