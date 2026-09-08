# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the set percent request module."""

# Set the activity pane to an explicit width percentage.
from api.terminal.models.panes.pane_gesture_request import PaneGestureRequest


class SetPanePercentRequest(PaneGestureRequest):
    """Represent set pane percent request."""

    percent: int
