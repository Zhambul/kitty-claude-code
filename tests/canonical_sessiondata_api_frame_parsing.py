# Copyright (c) 2026 Zhambyl Yermagambet
"""Canonical sessiondata api frame parsing."""

from __future__ import annotations

import json


def frame_body(frame: str) -> dict:
    """Decode the data line in an SSE frame.

    Returns:
        The JSON object from the first data line.

    Raises:
        AssertionError: If the frame has no data line.

    """
    for line in frame.splitlines():
        if line.startswith("data: "):
            return json.loads(line[len("data: ") :])
    raise AssertionError(frame)


def frame_id(frame: str) -> int:
    """Read the numeric identity in an SSE frame.

    Returns:
        The integer from the first identity line.

    Raises:
        AssertionError: If the frame has no identity line.

    """
    for line in frame.splitlines():
        if line.startswith("id: "):
            return int(line[len("id: ") :])
    raise AssertionError(frame)


def assert_ready_frame(frame: str) -> None:
    """Verify one ready frame and its boot identity."""
    assert "event: ready" in frame
    assert frame_body(frame) == {"boot_id": "boot-one"}
