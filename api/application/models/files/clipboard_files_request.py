# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the clipboard files request module."""

# Basenames of files pasted as zero-byte promises.
from typing import Annotated

from pydantic import BaseModel, Field


class ClipboardFilesRequest(BaseModel):
    """Represent clipboard files request."""

    names: Annotated[tuple[str, ...], Field(min_length=1)]
    session_id: str | None = None
