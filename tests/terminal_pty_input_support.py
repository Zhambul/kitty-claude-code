# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide input doubles for PTY terminal tests."""

from __future__ import annotations

from typing import Never

DENIED_PROCESS_ID = 731
type TerminalInputEvent = tuple[str, bytes] | tuple[str, int, float]


def record_terminal_write(events: list[TerminalInputEvent], payload: bytes) -> bool:
    """Record one terminal write.

    Returns:
        True for the recorded write.

    """
    events.append(("write", payload))
    return True


def record_screen_wait(events: list[TerminalInputEvent], revision: int, timeout: float) -> bool:
    """Record one terminal screen wait.

    Returns:
        True without waiting for a screen change.

    """
    events.append(("paint", revision, timeout))
    return True


def record_inserted_payload(events: list[bytes], payload: bytes) -> bool:
    """Record one inserted payload.

    Returns:
        True for the recorded insertion.

    """
    events.append(payload)
    return True


class DeniedProcess:
    """Simulate an operating-system denial of process details."""

    pid = DENIED_PROCESS_ID

    def children(self, *, recursive: bool) -> tuple[()]:
        """Return no child processes after a recursive request.

        Returns:
            No child processes after a recursive request.

        Raises:
            AssertionError: If the request is not recursive.

        """
        if not recursive:
            msg = "the process scan must be recursive"
            raise AssertionError(msg)
        return ()

    def cmdline(self) -> Never:
        """Raise the process-details denial.

        Raises:
            SystemError: For every request for command details.

        """
        msg = "the operating system denied process details"
        raise SystemError(msg)
