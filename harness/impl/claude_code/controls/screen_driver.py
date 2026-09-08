# Copyright (c) 2026 Zhambyl Yermagambet
"""Shared mechanics for Claude Code's screen-verified dialog drivers."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

    from domain.ids import WindowId
    from harness.impl.claude_code.controls.screen_protocols import (
        ScreenDriver,
    )


POLL_SECONDS = 0.15
SCREEN_LIMIT = 2000


def poll_until(
    screen_driver: ScreenDriver,
    window_id: WindowId,
    predicate: Callable[[str], object],
    timeout: float,
    sleep: Callable[[float], None] = time.sleep,
) -> tuple[str, bool]:
    """Return the poll until.

    Returns:
        Poll until.

    """
    deadline = time.monotonic() + timeout
    screen = screen_driver.read_text(window_id) or ""
    while not predicate(screen):
        if time.monotonic() >= deadline:
            return screen, False
        sleep(POLL_SECONDS)
        screen = screen_driver.read_text(window_id) or ""
    return screen, True


class StepError(Exception):
    """Represent step error."""

    def __init__(self, step: str, detail: str = "", screen: str | None = None) -> None:
        """Initialize the object."""
        super().__init__(f"{step}: {detail}" if detail else step)
        self.step = step
        self.screen = screen


def failure_detail(step_error: StepError) -> str:
    """Keep a bounded native screen with a verified driver failure.

    Returns:
        Text result.

    """
    if not step_error.screen:
        return str(step_error)
    screen_tail = step_error.screen[-SCREEN_LIMIT:]
    return f"{step_error}; screen={screen_tail!r}"
