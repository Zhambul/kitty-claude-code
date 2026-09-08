# Copyright (c) 2026 Zhambyl Yermagambet
"""Global harness usage checks."""

from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING

from pytest_bdd import parsers, then

from sdk.client import BaqylauClient, wait_for
from tests.e2e.steps import usage_checks

if TYPE_CHECKING:
    from tests.e2e.testkit.policy import WaitPolicy


@then(parsers.parse("global usage for {harness} has at least {count:d} window"))
def global_usage_has_windows(
    client: BaqylauClient,
    wait_policy: WaitPolicy,
    harness: str,
    count: int,
) -> None:
    """Process global usage has windows."""
    wait_for(
        f"global usage for {harness!r} to have at least {count} window",
        partial(usage_checks.rows_with_windows, client, harness, count),
        timeout=wait_policy.background,
    )


@then(parsers.parse("each global usage window for {harness} has a positive duration"))
def global_usage_windows_have_positive_duration(
    client: BaqylauClient,
    wait_policy: WaitPolicy,
    harness: str,
) -> None:
    """Process global usage windows have positive duration."""
    wait_for(
        f"each global usage window for {harness!r} to have a positive duration",
        partial(usage_checks.windows_with_positive_duration, client, harness),
        timeout=wait_policy.background,
    )


@then(parsers.parse("each global usage window for {harness} has a valid percentage"))
def global_usage_windows_have_valid_percentage(
    client: BaqylauClient,
    wait_policy: WaitPolicy,
    harness: str,
) -> None:
    """Process global usage windows have valid percentage."""
    wait_for(
        f"each global usage window for {harness!r} to have a percentage from 0 to 100",
        partial(usage_checks.windows_with_valid_percentage, client, harness),
        timeout=wait_policy.background,
    )


@then(parsers.parse("global usage window keys for {harness} are unique per account"))
def global_usage_window_keys_are_unique(
    client: BaqylauClient,
    wait_policy: WaitPolicy,
    harness: str,
) -> None:
    """Process global usage window keys are unique."""
    wait_for(
        f"global usage for {harness!r} to have unique window keys per account",
        partial(usage_checks.rows_with_unique_window_keys, client, harness),
        timeout=wait_policy.background,
    )
