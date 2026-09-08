# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the error response module."""

# The ONE error body this server sends, for every status, from every plane —
# written down so /openapi.yaml describes it too (api/responses.py).
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Represent error response."""

    error: str
