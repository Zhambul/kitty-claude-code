# Copyright (c) 2026 Zhambyl Yermagambet
"""Wait helpers for Codex transcript backtrack actions."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

from harness.impl.codex.controls import backtrack_errors

if TYPE_CHECKING:
    from collections.abc import Callable

    from domain.ids import WindowId
    from harness.impl.codex.controls.composer import ComposerControlDriver as Driver

POLL_SECONDS = 0.1
STEP_TIMEOUT_SECONDS = 10.0
RESTORE_TIMEOUT_SECONDS = 30.0
OPEN_STEP = "open"


def wait_for(
    read: Callable[[], str | None],
    predicate: Callable[[str | None], bool],
    sleep: Callable[[float], None],
    *,
    timeout_seconds: float = STEP_TIMEOUT_SECONDS,
) -> str | None:
    """Wait for a screen that meets the predicate.

    Returns:
        The screen, or none when it does not meet the predicate.

    """
    deadline = time.monotonic() + timeout_seconds
    latest = read()
    while not predicate(latest) and time.monotonic() < deadline:
        sleep(POLL_SECONDS)
        latest = read()
    return latest if predicate(latest) else None


def selection_screen(driver: Driver, window_id: WindowId) -> str | None:
    """Return the ANSI screen, or the plain screen if it has no ANSI data.

    Returns:
        The selected screen, or none when no screen is available.

    """
    return driver.read_text(window_id, ansi=True) or driver.read_text(window_id)


def send_escape(driver: Driver, window_id: WindowId, failure_detail: str) -> None:
    """Send one required Escape key.

    Raises:
        BacktrackError: If the terminal rejects the key.

    """
    if not driver.send_key(window_id, "escape"):
        raise backtrack_errors.BacktrackError(OPEN_STEP, failure_detail)


def require_screen(
    read: Callable[[], str | None],
    predicate: Callable[[str | None], bool],
    sleep: Callable[[float], None],
    failure_detail: str,
) -> None:
    """Wait for one required transcript screen.

    Raises:
        BacktrackError: If the screen does not appear.

    """
    if wait_for(read, predicate, sleep) is None:
        raise backtrack_errors.BacktrackError(OPEN_STEP, failure_detail)
