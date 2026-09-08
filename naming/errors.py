# Copyright (c) 2026 Zhambyl Yermagambet
"""Typed failures for automatic session naming."""

from inference.errors import ModelUnavailableError


class MissingSessionPromptError(ModelUnavailableError):
    """Report that a session has no semantic user prompt."""

    def __init__(self) -> None:
        """Create a missing-prompt failure."""
        super().__init__("session has no semantic user prompt")


class EmptyModelTitleError(ModelUnavailableError):
    """Report that a model returned no usable title."""

    def __init__(self) -> None:
        """Create an empty-title failure."""
        super().__init__("model returned an empty title")


class ShortModelTitleError(ModelUnavailableError):
    """Report that a model title has too few words."""

    def __init__(self) -> None:
        """Create a short-title failure."""
        super().__init__("model returned fewer than three title words")


class MissingHarnessPluginError(ValueError):
    """Report a session that has no attached harness plugin."""

    def __init__(self, session_id: str) -> None:
        """Create the failure for the specified session."""
        super().__init__(f"session has no attached harness plugin: {session_id}")


class InvalidRenameResultError(TypeError):
    """Report an invalid result from a rename control."""

    def __init__(self) -> None:
        """Create an invalid-result failure."""
        super().__init__("rename control returned a message delivery result")


class TerminalRenameError(RuntimeError):
    """Report a terminal tab rename failure."""

    def __init__(self, reason: str | None) -> None:
        """Create the failure with a terminal reason or a default reason."""
        super().__init__(reason or "terminal title was not changed")
