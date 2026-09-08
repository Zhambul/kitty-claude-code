# Copyright (c) 2026 Zhambyl Yermagambet
"""Stored token usage values and their reporting scope."""

from dataclasses import dataclass
from enum import StrEnum

from domain.stored import STORED


class UsageScope(StrEnum):
    """Identify the scope of one usage report."""

    SESSION = "session"
    ACTOR = "actor"
    TURN = "turn"
    OPERATION = "operation"


@dataclass(frozen=True)
class TokenUsage:
    """Hold nonnegative token counts for one usage report."""

    __pydantic_config__ = STORED

    input_tokens: int = 0
    output_tokens: int = 0
    cache_read_tokens: int = 0
    cache_write_tokens: int = 0
    one_hour_cache_write_tokens: int = 0

    def __post_init__(self) -> None:
        """Reject negative token counts.

        Raises:
            ValueError: If an input value is not valid.

        """
        token_counts = (
            self.input_tokens,
            self.output_tokens,
            self.cache_read_tokens,
            self.cache_write_tokens,
            self.one_hour_cache_write_tokens,
        )
        if any(token_count < 0 for token_count in token_counts):
            message = "token counts cannot be negative"
            raise ValueError(message)

    def __add__(self, token_usage: "TokenUsage") -> "TokenUsage":
        """Add the corresponding counts from two usage reports.

        Returns:
            The add.

        """
        return TokenUsage(
            input_tokens=self.input_tokens + token_usage.input_tokens,
            output_tokens=self.output_tokens + token_usage.output_tokens,
            cache_read_tokens=self.cache_read_tokens + token_usage.cache_read_tokens,
            cache_write_tokens=self.cache_write_tokens + token_usage.cache_write_tokens,
            one_hour_cache_write_tokens=(self.one_hour_cache_write_tokens + token_usage.one_hour_cache_write_tokens),
        )
