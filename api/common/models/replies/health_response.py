# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the health response module."""

# Who is answering on this port.
from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Represent health response."""

    process_id: int
