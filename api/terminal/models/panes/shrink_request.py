# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the shrink request module."""

# Shrink the activity pane (columns defaults server-side).
from api.terminal.models.panes.pane_gesture_request import PaneGestureRequest


class ShrinkPaneRequest(PaneGestureRequest):
    """Represent shrink pane request."""

    columns: int | None = None
