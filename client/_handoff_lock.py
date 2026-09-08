# Copyright (c) 2026 Zhambyl Yermagambet
"""Coordinate one live terminal pane through its lock file."""

from __future__ import annotations

import fcntl
import os
import pathlib

PRIVATE_FILE_MODE = 0o600


class PaneLock:
    """Keep the pane lock for this process lifetime."""

    def __init__(self) -> None:
        """Initialize an unclaimed lock."""
        self._descriptor: int | None = None

    def claim(self, path: str) -> bool:
        """Claim one lock path, if no pane has it.

        Returns:
            True if this process acquired the lock.

        """
        if self._descriptor is not None:
            return False
        try:
            descriptor = _claim_descriptor(path)
        except OSError:
            return False
        self._descriptor = descriptor
        return True


pane_lock = PaneLock()


def _claim_descriptor(path: str) -> int:
    flags = os.O_CREAT | os.O_TRUNC | os.O_WRONLY
    descriptor = os.open(path, flags, PRIVATE_FILE_MODE)
    try:
        fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        os.close(descriptor)
        raise
    return descriptor


def pane_is_running(path: str) -> bool:
    """Return true when a pane holds the lock.

    Returns:
        True when a pane holds the lock.

    """
    try:
        probe = pathlib.Path(path).open("a", encoding="utf-8")  # noqa: SIM115 -- The with block below separates open errors from lock errors.
    except OSError:
        return False
    with probe:
        try:
            fcntl.flock(probe, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            return True
    return False
