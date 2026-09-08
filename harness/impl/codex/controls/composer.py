# Copyright (c) 2026 Zhambyl Yermagambet
"""Control Codex's native prompt composer."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, Protocol, override

from harness.contract import ComposerDriver, HarnessComposer
from harness.impl.codex.controls import composer_state
from harness.models.probe import (
    TerminalInputState,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from domain.ids import WindowId

POLL_SECONDS = 0.1
CLEAR_TIMEOUT_SECONDS = 3.0
SCREEN_TAIL_CHARACTER_LIMIT = 1_200


class ComposerError(Exception):
    """A prompt composer action did not reach its checked state."""


class ComposerControlDriver(Protocol):
    """Read a Codex composer and send its clear keys."""

    def read_text(
        self,
        window_id: WindowId,
        extent: str = "screen",
        *,
        ansi: bool = False,
    ) -> str | None:
        """Read terminal text."""
        ...

    def send_key(self, window_id: WindowId, *keys: str) -> bool:
        """Send terminal keys."""
        ...


def clear(
    composer_control_driver: ComposerControlDriver,
    window_id: WindowId,
    *,
    sleep: Callable[[float], None] = time.sleep,
) -> None:
    """Clear the complete Codex draft and check the empty composer.

    Raises:
        ComposerError: If a terminal composer operation fails.

    """
    deadline = time.monotonic() + CLEAR_TIMEOUT_SECONDS
    screen = composer_control_driver.read_text(window_id)
    while not composer_state.empty(screen) and time.monotonic() < deadline:
        screen = _clear_line(composer_control_driver, window_id, sleep)
    if not composer_state.empty(screen):
        observed = (screen or "")[-SCREEN_TAIL_CHARACTER_LIMIT:]
        message = f"the Codex composer did not become empty; screen={observed!r}"
        raise ComposerError(
            message,
        )


def _clear_line(
    composer_control_driver: ComposerControlDriver,
    window_id: WindowId,
    sleep: Callable[[float], None],
) -> str | None:
    # Codex's kill shortcuts apply to one logical line. Clear both sides
    # of the cursor, then join the preceding line and repeat.
    if not composer_control_driver.send_key(window_id, "ctrl+u", "ctrl+k"):
        message = "the draft clear key was not delivered"
        raise ComposerError(message)
    sleep(POLL_SECONDS)
    screen = composer_control_driver.read_text(window_id)
    if not composer_state.empty(screen):
        if not composer_control_driver.send_key(window_id, "backspace"):
            message = "the draft join key was not delivered"
            raise ComposerError(message)
        sleep(POLL_SECONDS)
        screen = composer_control_driver.read_text(window_id)
    return screen


class CodexComposer(HarnessComposer):
    """Represent codex composer."""

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
        screen = composer_driver.read_text(window_id)
        text = composer_state.typed(screen)
        if text is None:
            return None
        return TerminalInputState(typed_text=text, suggestion=None)

    @override
    def clear(self, composer_driver: ComposerDriver, window_id: WindowId) -> None:
        """Clear clear."""
        clear(composer_driver, window_id)

    def insert(self, composer_driver: ComposerDriver, window_id: WindowId, text: str) -> None:
        """Return the insert.

        Raises:
            ComposerError: If a terminal composer operation fails.

        """
        if not text:
            return
        if not composer_driver.insert_text(window_id, text, paste=True):
            message = "the Codex draft was not inserted"
            raise ComposerError(message)
        self._wait_for(composer_driver, window_id, text)

    @override
    def submit(self, composer_driver: ComposerDriver, window_id: WindowId, text: str) -> None:
        """Submit.

        Raises:
            ComposerError: If a terminal composer operation fails.

        """
        if not composer_driver.submit_text(window_id, text, paste=True):
            message = "the Codex message was not delivered"
            raise ComposerError(message)

    def _wait_for(
        self,
        composer_driver: ComposerDriver,
        window_id: WindowId,
        expected: str,
    ) -> None:
        deadline = time.monotonic() + CLEAR_TIMEOUT_SECONDS
        while time.monotonic() < deadline:
            state = self.read(composer_driver, window_id)
            if state is not None and state.typed_text == expected:
                return
            time.sleep(POLL_SECONDS)
        state = self.read(composer_driver, window_id)
        observed = None if state is None else state.typed_text
        message = f"the Codex composer did not contain the expected draft; observed={observed!r}"
        raise ComposerError(
            message,
        )
