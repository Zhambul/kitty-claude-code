# Copyright (c) 2026 Zhambyl Yermagambet
"""Deterministic checks for browser E2E usage selection."""

from decimal import Decimal

import pytest

from api.common.models.values.usage_row import UsageRowResponse, UsageWindowResponse
from harness.models.usage import (
    UsageWindowScope,
)
from tests.e2e.testkit.browser import default_model_usage_window

USAGE_PERCENT = 21
USAGE_RESET_TIME = 2_000_000_000
WEEKLY_DURATION_MINUTES = 10_080
CLAUDE_HARNESS = "claude_code"
FABLE_MODEL_ID = "fable"


def _row(
    *,
    collection_error: str | None = None,
    account_id: str | None = None,
    switchable: bool = False,
) -> UsageRowResponse:
    return UsageRowResponse(
        harness=CLAUDE_HARNESS,
        account_id=account_id,
        display_name="claude",
        switchable=switchable,
        default_for_launch=True,
        plan="team",
        windows=(
            UsageWindowResponse(
                key="seven_day_fable",
                label="7d fable",
                used_percent=Decimal(USAGE_PERCENT),
                resets_at=USAGE_RESET_TIME,
                duration_minutes=WEEKLY_DURATION_MINUTES,
                scope=UsageWindowScope.MODEL,
                model_id=FABLE_MODEL_ID,
            ),
        ),
        scheduling_score=None,
        scheduling_allowed=False,
        limit=None,
        authentication_error=None,
        collection_error=collection_error,
    )


def test_usage_selection_fails_when_refresh() -> None:
    """Verify usage selection fails when refresh failed."""
    with pytest.raises(
        AssertionError,
        match="usage refresh failed: claude_code: profile refresh failed",
    ):
        default_model_usage_window(
            (_row(collection_error="profile refresh failed"),),
            CLAUDE_HARNESS,
            FABLE_MODEL_ID,
        )


def test_usage_selection_waits_for_initial() -> None:
    """Verify usage selection waits for initial publication."""
    assert default_model_usage_window((), CLAUDE_HARNESS, FABLE_MODEL_ID) is None


def test_usage_selection_retries_transient_probe() -> None:
    """Verify usage selection retries a transient probe timeout."""
    assert (
        default_model_usage_window(
            (_row(collection_error="usage probe timed out"),),
            CLAUDE_HARNESS,
            FABLE_MODEL_ID,
        )
        is None
    )


def test_usage_selection_rejects_claude_account() -> None:
    """Verify usage selection rejects a claude account selector."""
    with pytest.raises(AssertionError, match="published an account selection"):
        default_model_usage_window(
            (_row(account_id="legacy-account", switchable=True),),
            "claude_code",
            "fable",
        )
