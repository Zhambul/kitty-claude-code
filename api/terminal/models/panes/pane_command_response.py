# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the pane command response module."""

# The gesture's verdict (handled=False: no session in this window).
from pydantic import BaseModel


class PaneCommandResponse(BaseModel):
    """Represent pane command response."""

    handled: bool
    succeeded: bool
    reason: str | None
