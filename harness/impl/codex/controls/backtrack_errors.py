# Copyright (c) 2026 Zhambyl Yermagambet
"""Errors from Codex transcript backtrack actions."""


class BacktrackError(Exception):
    """A native backtrack step did not reach its verified screen state."""

    def __init__(self, step: str, detail: str) -> None:
        """Initialize the object."""
        super().__init__(f"{step}: {detail}")
        self.step = step
        self.detail = detail
