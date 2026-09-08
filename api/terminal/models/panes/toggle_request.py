# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the toggle request module."""

# Toggle the session panes.
from api.terminal.models.panes.pane_gesture_request import PaneGestureRequest


class TogglePanesRequest(PaneGestureRequest):
    """Represent toggle panes request."""
