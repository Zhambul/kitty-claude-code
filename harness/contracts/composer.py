# Copyright (c) 2026 Zhambyl Yermagambet
"""Define native prompt-composer contracts."""

from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    from domain.ids import WindowId
    from harness.models.probe import TerminalInputState
    from terminal.contract import TerminalPlugin


class _ComposerReadDriver(typing.Protocol):
    """Read terminal text and dimensions for a composer."""

    terminal: TerminalPlugin

    def read_text(
        self,
        window_id: WindowId,
        extent: str = "screen",
        *,
        ansi: bool = False,
    ) -> str | None:
        """Read terminal text."""
        ...

    def lines(self, window_id: WindowId) -> int | None:
        """Return the terminal line count."""
        ...


class _ComposerWriteDriver(typing.Protocol):
    """Send keys and text to a prompt composer."""

    def send_key(self, window_id: WindowId, *keys: str) -> bool:
        """Send keys."""
        ...

    def insert_text(self, window_id: WindowId, text: str, *, paste: bool = True) -> bool:
        """Insert text."""
        ...

    def submit_text(self, window_id: WindowId, text: str, *, paste: bool = True) -> bool:
        """Submit text."""
        ...

    def send_text(self, window_id: WindowId, text: str) -> bool:
        """Send text."""
        ...

    def paste_text(self, window_id: WindowId, text: str) -> bool:
        """Paste text."""
        ...

    def resize_lines(self, window_id: WindowId, cells: int) -> bool:
        """Resize the terminal by lines."""
        ...


class ComposerDriver(_ComposerReadDriver, _ComposerWriteDriver, typing.Protocol):
    """Read and change the terminal for a prompt composer."""


class HarnessComposer(typing.Protocol):
    """Read and change one harness native prompt composer."""

    def read(
        self,
        composer_driver: ComposerDriver,
        window_id: WindowId,
    ) -> TerminalInputState | None:
        """Read the native prompt composer."""
        ...

    def clear(self, composer_driver: ComposerDriver, window_id: WindowId) -> None:
        """Clear the prompt composer."""
        ...

    def insert(self, composer_driver: ComposerDriver, window_id: WindowId, text: str) -> None:
        """Insert text into the prompt composer."""
        ...

    def submit(self, composer_driver: ComposerDriver, window_id: WindowId, text: str) -> None:
        """Submit text from the prompt composer."""
        ...
