# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the hide directory request module."""

# Hide one directory from the session list.
from pydantic import BaseModel


class HideDirectoryRequest(BaseModel):
    """Represent hide directory request."""

    working_directory: str
