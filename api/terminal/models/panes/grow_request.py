# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the grow request module."""

# Grow the activity pane (columns defaults server-side).
from api.terminal.models.panes.pane_gesture_request import PaneGestureRequest


class GrowPaneRequest(PaneGestureRequest):
    """Represent grow pane request."""

    columns: int | None = None
