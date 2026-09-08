# Copyright (c) 2026 Zhambyl Yermagambet
"""Record usage base."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field

from harness.impl.claude_code.canonical.record_common import FOREIGN


class UsageOutputTokensDetails(BaseModel):
    """Represent usage output tokens details."""

    model_config = FOREIGN
    thinking_tokens: int | float


class UsageServerToolUse(BaseModel):
    """Represent usage server tool use."""

    model_config = FOREIGN
    web_search_requests: int | float
    web_fetch_requests: int | float


class UsageCacheCreation(BaseModel):
    """Represent usage cache creation."""

    model_config = FOREIGN
    ephemeral_one_hour_input_tokens: int | float = Field(
        validation_alias="ephemeral_1h_input_tokens",
    )
    ephemeral_five_minute_input_tokens: int | float = Field(
        validation_alias="ephemeral_5m_input_tokens",
    )


class UsageIterationType(StrEnum):
    """Represent usage iteration type."""

    MESSAGE = "message"
    FALLBACK_MESSAGE = "fallback_message"


class UsageIteration(BaseModel):
    """Represent usage iteration."""

    model_config = FOREIGN
    input_tokens: int | float
    output_tokens: int | float
    cache_read_input_tokens: int | float
    cache_creation_input_tokens: int | float
    cache_creation: UsageCacheCreation
    type: UsageIterationType
    model: str | None = None


class UsageServiceTier(StrEnum):
    """Represent usage service tier."""

    STANDARD = "standard"


class UsageSpeed(StrEnum):
    """Represent usage speed."""

    STANDARD = "standard"
