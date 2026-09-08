# Copyright (c) 2026 Zhambyl Yermagambet
"""Own usage payloads models."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from harness.impl.codex.canonical.record_config import FOREIGN
from harness.impl.codex.ids_conversation_types import CodexResponseId, CodexTurnId
from harness.impl.codex.ids_session_types import CodexSessionId


class TokenUsageBlock(BaseModel):
    """One `total_token_usage` / `last_token_usage` snapshot."""

    model_config = FOREIGN
    input_tokens: int | None = None
    output_tokens: int | None = None
    cached_input_tokens: int | None = None
    cache_write_input_tokens: int | None = None
    reasoning_output_tokens: int | None = None
    total_tokens: int | None = None


class TokenUsageRecordPayload(BaseModel):
    """Read usage details that also occur in token count events."""

    model_config = FOREIGN
    thread_id: CodexSessionId
    turn_id: CodexTurnId
    session_id: CodexSessionId
    root_turn_id: CodexTurnId
    response_id: CodexResponseId
    usage: TokenUsageBlock
    turn_token_usage: TokenUsageBlock
    thread_token_usage: TokenUsageBlock


class TokenCountInfo(BaseModel):
    """Represent token count info."""

    model_config = FOREIGN
    total_token_usage: TokenUsageBlock | None = None
    last_token_usage: TokenUsageBlock | None = None
    model_context_window: int | None = None


class RateLimitWindow(BaseModel):
    """Represent rate limit window."""

    model_config = FOREIGN
    used_percent: float | None = None
    window_minutes: int | None = None
    resets_at: int | None = None


class RateLimitCredits(BaseModel):
    """Represent rate limit credits."""

    model_config = FOREIGN
    has_credits: bool | None = None
    unlimited: bool | None = None
    balance: float | int | None = None


class RateLimitsBlock(BaseModel):
    """Represent rate limits block."""

    model_config = FOREIGN
    plan_type: str | None = None
    primary: RateLimitWindow | None = None
    secondary: RateLimitWindow | None = None
    limit_id: str | None = None
    limit_name: str | None = None
    individual_limit: str | int | float | None = None
    credits: RateLimitCredits | None = None
    rate_limit_reached_type: str | None = None
    spend_control_reached: bool | None = None


class TokenCountPayload(BaseModel):
    """Represent token count payload.

    A `token_count` event_msg payload. `info` is null on a rate-limit-only
        event (events.py _ev_token_count); `rate_limits` rides the same event on
        an independent nullable field (events.py rate_limits()).
    """

    model_config = FOREIGN
    type: Literal["token_count"] = "token_count"
    usage_info: TokenCountInfo | None = Field(default=None, alias="info")
    rate_limits: RateLimitsBlock | None = None
