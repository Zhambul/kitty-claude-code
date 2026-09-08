# Copyright (c) 2026 Zhambyl Yermagambet
"""The application-wide inference contract, independent of any harness."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ModelPromptRequest:
    """Hold one prompt and its audit session identifier."""

    prompt: str
    session_id: str = ""


@dataclass(frozen=True)
class ModelPromptResponse:
    """Hold the text returned by one model request."""

    text: str


class Model(Protocol):
    """Send one prompt to a model."""

    def send(self, model_prompt_request: ModelPromptRequest) -> ModelPromptResponse:
        """Send one prompt and return its text response."""
        ...


class ModelFactory(Protocol):
    """Provide models by application size class."""

    def big(self) -> Model:
        """Return the configured large model."""
        ...

    def mid(self) -> Model:
        """Return the configured middle model."""
        ...

    def small(self) -> Model:
        """Return the configured small model."""
        ...
