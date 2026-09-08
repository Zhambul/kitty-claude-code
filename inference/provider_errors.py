# Copyright (c) 2026 Zhambyl Yermagambet
"""Typed failures from one inference provider attempt."""

from inference.errors import ProviderUnavailableError


class ProviderStartError(ProviderUnavailableError):
    """Report that a provider process did not start."""

    def __init__(self, reason: str | None) -> None:
        """Create a start failure with a provider reason."""
        super().__init__(reason or "model process did not start", stage="start")


class ProviderTimeoutError(ProviderUnavailableError):
    """Report that a provider did not finish before its deadline."""

    def __init__(self) -> None:
        """Create a provider timeout failure."""
        super().__init__("model response timed out", stage="wait")


class ProviderOutputReadError(ProviderUnavailableError):
    """Report that terminal output was not readable."""

    def __init__(self, reason: str | None) -> None:
        """Create an output read failure with a provider reason."""
        super().__init__(reason or "model output was not readable", stage="read output")


class ProviderOutputParseError(ProviderUnavailableError):
    """Report that terminal output had no usable result."""

    def __init__(self, error: ProviderUnavailableError, output: str) -> None:
        """Create a parse failure and keep the terminal output."""
        super().__init__(str(error), stage="parse output", output=output)


class ProviderAvailabilityError(ProviderUnavailableError):
    """Report an availability limit in provider output."""

    def __init__(self) -> None:
        """Create an availability-limit failure."""
        super().__init__("provider reported an availability limit")


class ProviderTitleShapeError(ProviderUnavailableError):
    """Report a title that does not have the requested shape."""

    def __init__(self) -> None:
        """Create a title-shape failure."""
        super().__init__("model returned a title outside the requested shape")


class ProviderTitleMissingError(ProviderUnavailableError):
    """Report output that has no structured title."""

    def __init__(self) -> None:
        """Create a missing-title failure."""
        super().__init__("model returned no structured title")
