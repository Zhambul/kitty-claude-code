# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the kitten client operations."""

import subprocess  # noqa: S404 -- Use the configured kitten executable for remote control.
from typing import Protocol

from terminal.impl.kitty.remote_constants import KITTEN_TIMEOUT_SECONDS, REMOTE_CONTROL_MARKER, TARGET_OPTION


class _KittyClient(Protocol):
    kitten: str | None

    @property
    def listen(self) -> str:
        """The remote-control socket address."""


class KittyClientOperations:
    """Provide kitten client operations."""

    def run(self: _KittyClient, *args: str) -> int:
        """Run a silenced kitten command.

        Returns:
            The command exit code, or one if the command cannot run.

        """
        if self.kitten is None:
            return 1
        try:
            return subprocess.run(  # noqa: S603 -- Pass remote-control arguments to kitten without a shell.
                [self.kitten, REMOTE_CONTROL_MARKER, TARGET_OPTION, self.listen, *args],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=KITTEN_TIMEOUT_SECONDS,
            ).returncode
        except (OSError, subprocess.SubprocessError):
            return 1

    def capture(self: _KittyClient, *args: str, timeout: float = KITTEN_TIMEOUT_SECONDS) -> str | None:
        """Run a kitten command and capture its text result.

        Returns:
            Decoded standard output, or None if the command is unavailable or fails.

        """
        if self.kitten is None:
            return None
        try:
            completed_process = subprocess.run(  # noqa: S603 -- Pass remote-control arguments to kitten without a shell.
                [self.kitten, REMOTE_CONTROL_MARKER, TARGET_OPTION, self.listen, *args],
                capture_output=True,
                check=False,
                timeout=timeout,
            )
        except (OSError, subprocess.SubprocessError):
            return None
        if completed_process.returncode != 0:
            return None
        return completed_process.stdout.decode("utf-8", "replace")
