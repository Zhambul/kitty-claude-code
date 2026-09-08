# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the recorded response module."""

# The telemetry-accepted reply.
from pydantic import BaseModel


class RecordedResponse(BaseModel):
    """Represent recorded response."""

    recorded: bool = True
