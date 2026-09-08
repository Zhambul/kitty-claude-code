# Copyright (c) 2026 Zhambyl Yermagambet
"""Map domain usage values to API models."""

from __future__ import annotations

from typing import TYPE_CHECKING

from api.common.models.values.token_usage import TokenUsageResponse
from api.common.models.values.usage_row import (
    UsageBlockResponse,
    UsageRowResponse,
    UsageWindowResponse,
)

if TYPE_CHECKING:
    from domain.usage import TokenUsage
    from harness.models.usage import (
        UsageRow,
    )


def token_usage(token_usage: TokenUsage) -> TokenUsageResponse:
    """Map token usage to its API model.

    Returns:
        The token usage response.

    """
    return TokenUsageResponse(
        input_tokens=token_usage.input_tokens,
        output_tokens=token_usage.output_tokens,
        cache_read_tokens=token_usage.cache_read_tokens,
        cache_write_tokens=token_usage.cache_write_tokens,
        one_hour_cache_write_tokens=token_usage.one_hour_cache_write_tokens,
    )


def usage_row(usage_row: UsageRow) -> UsageRowResponse:
    """Map one usage row to its API model.

    Returns:
        The usage row response.

    """
    return UsageRowResponse(
        harness=usage_row.harness,
        account_id=usage_row.account_id,
        display_name=usage_row.display_name,
        switchable=usage_row.switchable,
        default_for_launch=usage_row.default_for_launch,
        plan=usage_row.plan,
        windows=tuple(
            UsageWindowResponse(
                key=window.key,
                label=window.label,
                used_percent=window.used_percent,
                resets_at=window.resets_at,
                duration_minutes=window.duration_minutes,
                scope=window.scope,
                model_id=window.model_name,
            )
            for window in usage_row.windows
        ),
        scheduling_score=usage_row.scheduling_score,
        scheduling_allowed=usage_row.scheduling_allowed,
        limit=(
            None
            if usage_row.limit is None
            else UsageBlockResponse(
                model_id=usage_row.limit.model_name,
                message=usage_row.limit.message,
                resets_at=usage_row.limit.resets_at,
            )
        ),
        authentication_error=usage_row.authentication_error,
        collection_error=usage_row.collection_error,
    )
