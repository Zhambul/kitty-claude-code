# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the view mode request module."""

# One session's chosen view mode.
from pydantic import BaseModel

from api.common.models.fields import RequiredText


class ViewModeRequest(BaseModel):
    """Represent view mode request."""

    view_mode: RequiredText
