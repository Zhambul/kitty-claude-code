# Copyright (c) 2026 Zhambyl Yermagambet
"""Control the native Claude Code question dialog."""

import contextlib
import time
from collections.abc import Callable

from domain.ids import WindowId
from harness.impl.claude_code.controls import ask_flow
from harness.impl.claude_code.controls.ask_models import AskContext, AskOutcome, AskRequest
from harness.impl.claude_code.controls.screen_protocols import AskScreenDriver

POLL_SECONDS = 0.15
DIALOG_MIN_LINES = 60


def drive(
    ask_screen_driver: AskScreenDriver,
    window_id: WindowId,
    ask_request: AskRequest,
    sleep: Callable[[float], None] = time.sleep,
) -> AskOutcome:
    """Drive one question dialog inside a usable viewport.

    Returns:
        The completed question dialog outcome.

    """
    context = AskContext(
        screen_driver=ask_screen_driver,
        window_id=window_id,
        sleep=sleep,
        questions=ask_request.questions,
    )
    current_lines = ask_screen_driver.lines(window_id)
    growth = 0 if current_lines is None else max(0, DIALOG_MIN_LINES - current_lines)
    viewport_grown = growth > 0 and ask_screen_driver.resize_lines(window_id, growth)
    with contextlib.ExitStack() as cleanup:
        if viewport_grown:
            cleanup.callback(ask_screen_driver.resize_lines, window_id, -growth)
            sleep(POLL_SECONDS)
        return ask_flow.drive_dialog(context, ask_request.answers, chat=ask_request.chat)
