# Copyright (c) 2026 Zhambyl Yermagambet
"""Support for composer hook tests."""

from domain.ids import (
    WindowId,
)
from tests.plugin_tests import support_terminal, vocabulary as fixture


def submission_marker_is_visible(
    frontend: support_terminal.SubmitProbeDriver,
    window_id: WindowId,
    marker: str,
) -> bool:
    """Check the input box for a submission marker.

    Returns:
        True if the window identity is set and the input box contains the marker.

    """
    return bool(window_id) and marker in frontend.box


def clipboard_has_no_image() -> bool:
    """Provide the clipboard-image probe result for text-only tests.

    Returns:
        False to report that no clipboard image is present.

    """
    return False


class ClearComposerDriver:
    """Model immediate or delayed composer screen updates."""

    terminal = None

    def __init__(self, lines: list[str], *, clear_is_delayed: bool = False) -> None:
        """Store the composer lines and choose immediate or delayed clearing."""
        self.lines = lines
        self.keys: list[str] = []
        self._clear_is_delayed = clear_is_delayed
        self._clear_is_pending = False
        self._reads: list[tuple[str, bool]] = []

    def read_text(
        self,
        _window: WindowId,
        extent: str = fixture.SCREEN,
        *,
        ansi: bool = False,
    ) -> str:
        """Record a screen read and apply any pending line removal.

        Returns:
            The composer screen with the remaining lines.

        """
        self._reads.append((extent, ansi))
        if self._clear_is_pending:
            self.lines.pop()
            self._clear_is_pending = False
        rule = fixture.DIVIDER_CHARACTER * fixture.DIVIDER_WIDTH
        content = "\n".join(self.lines)
        return f"{rule}\n\u276f\u00a0{content}\n{rule}"

    def send_key(self, _window: WindowId, *pressed: str) -> bool:
        """Record keys and clear a line immediately or on the next read.

        Returns:
            True to report successful key delivery.

        """
        self.keys.extend(pressed)
        if pressed == (fixture.CLEAR_AFTER_CURSOR_KEY,) and self.lines:
            if self._clear_is_delayed:
                self._clear_is_pending = True
            else:
                self.lines.pop()
        return True
