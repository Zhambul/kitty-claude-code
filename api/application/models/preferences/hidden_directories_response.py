# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the hidden directories response module."""

# The updated hidden-directory map.
from collections.abc import Mapping

from pydantic import BaseModel


class HiddenDirectoriesResponse(BaseModel):
    """Represent hidden directories response."""

    hidden: Mapping[str, float]
