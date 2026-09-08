# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the reset request module."""

# Reset the activity pane to the configured width.
from api.terminal.models.panes.pane_gesture_request import PaneGestureRequest


class ResetPaneRequest(PaneGestureRequest):
    """Represent reset pane request."""
