# Copyright (c) 2026 Zhambyl Yermagambet
"""Read the current Claude Code composer state."""

from domain.ids import WindowId
from harness.impl.claude_code import suggestion, suggestion_screen
from harness.impl.claude_code.controls.screen_protocols import ScreenDriver
from harness.models.probe import (
    TerminalInputState,
)


def read_composer_state(
    screen_driver: ScreenDriver,
    window_id: WindowId,
) -> TerminalInputState | None:
    """Read the current composer text and suggestion.

    Returns:
        The current composer state, or ``None`` when it is not readable.

    """
    screen = screen_driver.read_text(window_id, ansi=True)
    if screen is None:
        screen = screen_driver.read_text(window_id)
    if screen is None:
        return None
    if not suggestion_screen.input_box_visible(screen):
        if suggestion_screen.composer_visible(screen):
            return TerminalInputState(typed_text="", suggestion=None)
        return None
    return TerminalInputState(
        typed_text=suggestion.typed(screen) or "",
        suggestion=suggestion.parse(screen),
    )
