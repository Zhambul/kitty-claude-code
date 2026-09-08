# Copyright (c) 2026 Zhambyl Yermagambet
"""Read and change the Claude Code prompt composer."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, override

from harness.contract import ComposerDriver, HarnessComposer
from harness.impl.claude_code import suggestion
from harness.impl.claude_code.composer_state import read_composer_state
from harness.impl.claude_code.controls import composer_clear, tui

if TYPE_CHECKING:
    from domain.ids import WindowId
    from harness.models.probe import TerminalInputState

CHANGE_TIMEOUT_SECONDS = 3.0
POLL_SECONDS = 0.1


class ComposerError(Exception):
    """A Claude composer action did not reach its checked state."""


def _insert_mode(composer_driver: ComposerDriver, window_id: WindowId) -> None:
    screen = composer_driver.read_text(window_id) or ""
    keys: tuple[str, ...]
    if "-- VISUAL --" in screen:
        keys = ("escape", "i")
    elif "-- NORMAL --" in screen:
        keys = ("i",)
    else:
        return
    if not composer_driver.send_key(window_id, *keys):
        message = "the Claude composer mode keys were not delivered"
        raise ComposerError(message)


class ClaudeCodeComposer(HarnessComposer):
    """Represent claude code composer."""

    @override
    def read(
        self,
        composer_driver: ComposerDriver,
        window_id: WindowId,
    ) -> TerminalInputState | None:
        """Return read.

        Returns:
            Read.

        """
        return read_composer_state(composer_driver, window_id)

    def clear(self, composer_driver: ComposerDriver, window_id: WindowId) -> None:
        """Clear the composer and verify that its input is empty.

        The screen and input helpers raise ComposerError if verification fails.

        """
        state = self._wait_for_readable(composer_driver, window_id)
        _insert_mode(composer_driver, window_id)
        composer_clear.clear_input(composer_driver, window_id, state.typed_text or "")
        self._wait_for(composer_driver, window_id, "")

    def insert(self, composer_driver: ComposerDriver, window_id: WindowId, text: str) -> None:
        """Return the insert.

        Raises:
            ComposerError: If a terminal composer operation fails.

        """
        if not text:
            return
        _insert_mode(composer_driver, window_id)
        if not composer_driver.insert_text(window_id, text, paste=True):
            message = "the Claude draft was not inserted"
            raise ComposerError(message)
        self._wait_for(composer_driver, window_id, suggestion.norm(text))

    @override
    def submit(self, composer_driver: ComposerDriver, window_id: WindowId, text: str) -> None:
        """Submit.

        Raises:
            ComposerError: If a terminal composer operation fails.

        """
        succeeded, _cleared_image = tui.type_command(composer_driver, window_id, text)
        if not succeeded:
            message = "the Claude message was not delivered"
            raise ComposerError(message)

    def _wait_for_readable(
        self,
        composer_driver: ComposerDriver,
        window_id: WindowId,
    ) -> TerminalInputState:
        deadline = time.monotonic() + CHANGE_TIMEOUT_SECONDS
        while time.monotonic() < deadline:
            state = self.read(composer_driver, window_id)
            if state is not None:
                return state
            time.sleep(POLL_SECONDS)
        message = "the Claude composer is not readable"
        raise ComposerError(message)

    def _wait_for(
        self,
        composer_driver: ComposerDriver,
        window_id: WindowId,
        expected: str,
    ) -> None:
        deadline = time.monotonic() + CHANGE_TIMEOUT_SECONDS
        while time.monotonic() < deadline:
            state = self.read(composer_driver, window_id)
            if state is not None and (state.typed_text or "") == expected:
                return
            time.sleep(POLL_SECONDS)
        state = self.read(composer_driver, window_id)
        observed = None if state is None else state.typed_text
        message = f"the Claude composer did not contain the expected draft; observed={observed!r}"
        raise ComposerError(
            message,
        )
