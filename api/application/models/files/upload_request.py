# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the upload request module."""

# One composer attachment as a JSON+base64 document (no multipart on purpose).
from pydantic import BaseModel, Field


class UploadRequest(BaseModel):
    """Represent upload request."""

    name: str
    mime: str = ""
    encoded_content: str = Field(alias="data")
    session_id: str | None = None
