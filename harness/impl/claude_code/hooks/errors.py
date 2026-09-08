# Copyright (c) 2026 Zhambyl Yermagambet
"""Define errors for incomplete Claude Code hook data."""


class MissingSessionIdError(ValueError):
    """Report a hook payload that has no session ID."""

    def __init__(self) -> None:
        """Initialize the error."""
        super().__init__("Claude Code hook payload has no session id")


class MissingAgentIdError(ValueError):
    """Report a subagent hook payload that has no agent ID."""

    def __init__(self, hook_name: str) -> None:
        """Initialize the error."""
        super().__init__(f"Claude Code {hook_name} payload has no agent id")


class MissingTranscriptPathError(ValueError):
    """Report a hook payload that has no transcript path."""

    def __init__(self) -> None:
        """Initialize the error."""
        super().__init__("Claude Code hook payload has no transcript path")
