# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the upload response module."""

# The staged attachment's absolute path for the @path mention.
from pydantic import BaseModel


class UploadResponse(BaseModel):
    """Represent upload response."""

    ok: bool = True
    path: str
    name: str
    mime: str
    is_image: bool
