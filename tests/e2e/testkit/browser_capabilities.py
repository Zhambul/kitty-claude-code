# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide browser capabilities."""

from __future__ import annotations

from tests.e2e.testkit import (
    browser_client_dependencies as client_dependencies,
    browser_model_dependencies as model_dependencies,
    browser_standard_dependencies as standard_dependencies,
)

regular_expressions = standard_dependencies.re

ACCOUNT_NAME = "account"


class BrowserPlanAction(standard_dependencies.StrEnum):
    """List the plan actions available in the browser."""

    approve = "approve"
    dismiss = "dismiss"
    feedback = "feedback"


def raise_usage_refresh_failure(
    rows: standard_dependencies.Sequence[model_dependencies.UsageRowResponse],
) -> None:
    """Raise for a failed usage refresh that will not resolve by waiting.

    Raises:
        AssertionError: If a collection error is not a timeout.

    """
    failures = [f"{row.harness}: {row.collection_error}" for row in rows if row.collection_error is not None]
    if failures and (not all("timed out" in failure.casefold() for failure in failures)):
        failure_summary = "; ".join(failures)
        msg = f"usage refresh failed: {failure_summary}"
        raise AssertionError(msg)


def default_harness_row(
    rows: standard_dependencies.Sequence[model_dependencies.UsageRowResponse], harness: str,
) -> model_dependencies.UsageRowResponse | None:
    """Return the one row for a default harness account.

    Returns:
        The default account row, or None if the harness has no row.

    Raises:
        AssertionError: If multiple rows or an account selection are present.

    """
    harness_rows = [row for row in rows if row.harness == harness]
    if not harness_rows:
        return None
    if len(harness_rows) != 1:
        msg = f"harness {harness!r} has {len(harness_rows)} usage rows"
        raise AssertionError(msg)
    row = harness_rows[0]
    if row.account_id is not None or row.switchable:
        msg = f"harness {harness!r} published an account selection"
        raise AssertionError(msg)
    return row


def account_locator(page: client_dependencies.Page, display_name: str) -> client_dependencies.Locator:
    """Return the dashboard account locator for one display name.

    Returns:
        The dashboard account locator for one display name.

    """
    account_cards = page.locator(".acct")
    account_names = page.locator(".aname")
    name_pattern = regular_expressions.compile(f"^{regular_expressions.escape(display_name)}$")
    selected_name = account_names.filter(has_text=name_pattern)
    return account_cards.filter(has=selected_name)


def usage_bar_locator(
    page: client_dependencies.Page, account: client_dependencies.Locator, label: str,
) -> client_dependencies.Locator:
    """Return the usage bar locator for one label.

    Returns:
        The usage bar locator for one label.

    """
    usage_bars = account.locator(".ubar")
    labels = page.locator(".ulabel")
    label_pattern = regular_expressions.compile(f"^{regular_expressions.escape(label)}$")
    selected_label = labels.filter(has_text=label_pattern)
    return usage_bars.filter(has=selected_label)


def is_weekly_account_window(window: model_dependencies.UsageWindowResponse) -> bool:
    """Return whether a window is the weekly account window.

    Returns:
        Whether a window is the weekly account window.

    """
    return window.scope == ACCOUNT_NAME and window.duration_minutes == 7 * 24 * 60


def is_requested_model_window(window: model_dependencies.UsageWindowResponse, model: str) -> bool:
    """Return whether a window belongs to the requested model.

    Returns:
        Whether a window belongs to the requested model.

    """
    return window.scope == "model" and window.model_id == model
