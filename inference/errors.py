# Copyright (c) 2026 Zhambyl Yermagambet
"""Typed failures from model inference."""


class ModelUnavailableError(RuntimeError):
    """No configured model provider can currently answer."""


class ProviderUnavailableError(RuntimeError):
    """One provider failed in a way that permits trying another provider."""

    def __init__(
        self,
        message: str,
        *,
        stage: str = "",
        output: str = "",
    ) -> None:
        """Create a provider failure with its execution stage and output."""
        super().__init__(message)
        self.stage = stage
        self.output = output


class ExecutableResolverConfigurationError(ValueError):
    """Report conflicting executable resolver configuration."""

    def __init__(self) -> None:
        """Create a resolver configuration failure."""
        super().__init__(
            "configure executable availability or resolution, not both",
        )
