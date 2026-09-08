# Copyright (c) 2026 Zhambyl Yermagambet
"""Convert harness window identifiers to terminal identifiers."""

from domain.ids import WindowId
from terminal.models.values import WindowId as NativeWindowId


def native_window_id(window_id: WindowId) -> NativeWindowId:
    """Convert a harness window identifier to a terminal identifier.

    Returns:
        The same identifier text with the terminal's identifier type.

    """
    return NativeWindowId(str(window_id))
