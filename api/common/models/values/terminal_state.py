# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the terminal state module."""

# Where a session is on screen, and what its own TUI is showing right now.
from pydantic import BaseModel


class TerminalInputStateResponse(BaseModel):
    """Represent terminal input state response."""

    typed_text: str | None
    suggestion: str | None


class TerminalStateResponse(BaseModel):
    """Represent terminal state response."""

    window_id: str | None
    input_state: TerminalInputStateResponse | None
