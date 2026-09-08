# Copyright (c) 2026 Zhambyl Yermagambet
"""Control the native Claude Code rewind dialog."""

import contextlib
import time
from collections.abc import Callable

from domain.ids import WindowId
from harness.impl.claude_code.controls import rewind_flow
from harness.impl.claude_code.controls.rewind_models import RewindContext, RewindOutcome, RewindRequest
from harness.impl.claude_code.controls.screen_protocols import RewindScreenDriver

DIALOG_MIN_LINES = 40
POLL_SECONDS = 0.15


def drive(
    rewind_screen_driver: RewindScreenDriver,
    window_id: WindowId,
    rewind_request: RewindRequest,
    sleep: Callable[[float], None] = time.sleep,
) -> RewindOutcome:
    """Run one native rewind inside a usable temporary viewport.

    Returns:
        The completed rewind result.

    """
    context = RewindContext(rewind_screen_driver, window_id, sleep)
    current_lines = rewind_screen_driver.lines(window_id)
    growth = 0 if current_lines is None else max(0, DIALOG_MIN_LINES - current_lines)
    viewport_grown = growth > 0 and rewind_screen_driver.resize_lines(window_id, growth)
    with contextlib.ExitStack() as cleanup:
        if viewport_grown:
            cleanup.callback(rewind_screen_driver.resize_lines, window_id, -growth)
            sleep(POLL_SECONDS)
        return rewind_flow.drive_menu(context, rewind_request)
