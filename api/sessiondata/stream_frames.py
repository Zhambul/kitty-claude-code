# Copyright (c) 2026 Zhambyl Yermagambet
"""Build the nonempty frames in one stream poll."""

from __future__ import annotations


def present_frames(*frames: str | None) -> tuple[str, ...]:
    """Return the nonempty frames in order.

    Returns:
        The nonempty frames in order.

    """
    return tuple(frame for frame in frames if frame is not None)
