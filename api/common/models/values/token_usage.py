# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the token usage module."""

# One actor's or one model's token consumption, as the scorebar reads it.
from pydantic import BaseModel


class TokenUsageResponse(BaseModel):
    """Represent token usage response."""

    input_tokens: int
    output_tokens: int
    cache_read_tokens: int
    cache_write_tokens: int
    one_hour_cache_write_tokens: int
