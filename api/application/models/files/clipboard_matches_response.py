# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the clipboard matches response module."""

# The host paths whose basenames matched exactly (empty on a miss).
from pydantic import BaseModel


class ClipboardMatchesResponse(BaseModel):
    """Represent clipboard matches response."""

    paths: tuple[str, ...]
