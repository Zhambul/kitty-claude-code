# Copyright (c) 2026 Zhambyl Yermagambet
"""Select usable harness accounts for named session specifications."""

from __future__ import annotations

from dataclasses import replace
from functools import partial
from typing import TYPE_CHECKING

import pytest

from sdk.client import WaitTimeoutError, wait_for
from tests.e2e.testkit import account_publishing
from tests.e2e.testkit.references import AccountSelectionRef

if TYPE_CHECKING:
    from api.common.models.values.usage_row import UsageRowResponse, UsageWindowResponse
    from tests.e2e.testkit.account_contexts import AccountSelectionContext

ACCOUNT_USAGE_WAIT_SECONDS = 15.0
FULL_USAGE_PERCENT = 100


def select_by_id(
    selection_context: AccountSelectionContext,
    session_name: str,
    account_id: str,
) -> None:
    """Select one published account by its stable identifier."""
    specification = selection_context.session_specs.get(session_name)
    selected = wait_for(
        f"harness {specification.harness!r} to publish account {account_id!r}",
        partial(account_publishing.configured_account, selection_context.client, specification.harness, account_id),
        timeout=selection_context.wait_policy.feed,
    )
    selection_context.account_selections.bind(
        f"{session_name} account",
        AccountSelectionRef(account_id, selected.display_name),
    )
    selection_context.session_specs.replace(session_name, replace(specification, account_id=account_id))


def select_available(
    selection_context: AccountSelectionContext,
    session_name: str,
    account_name: str,
) -> None:
    """Select the best account that can launch the session.

    Raises:
        AssertionError: If the selected account has no stable identifier.

    """
    specification = selection_context.session_specs.get(session_name)
    rows = wait_for(
        f"harness {specification.harness!r} to publish switchable accounts",
        partial(account_publishing.published_accounts, selection_context.client, specification.harness),
        timeout=selection_context.wait_policy.feed,
    )
    try:
        rows = wait_for(
            f"harness {specification.harness!r} to publish account capacity",
            partial(account_publishing.measured_accounts, selection_context.client, specification.harness),
            timeout=min(selection_context.wait_policy.feed, ACCOUNT_USAGE_WAIT_SECONDS),
        )
    except WaitTimeoutError:
        rows = account_publishing.switchable_rows(selection_context.client, specification.harness)
    selected = best_available(rows, specification.model, specification.harness)
    selected_account_id = selected.account_id
    if selected_account_id is None:
        message = "the selected switchable account has no identity"
        raise AssertionError(message)
    selection_context.account_selections.bind(
        account_name,
        AccountSelectionRef(selected_account_id, selected.display_name),
    )
    selection_context.session_specs.replace(
        session_name,
        replace(specification, account_id=selected_account_id),
    )


def best_available(
    rows: tuple[UsageRowResponse, ...],
    model: str | None,
    harness: str,
) -> UsageRowResponse:
    """Return the highest-priority account that can launch the model.

    Returns:
        The selected account row.

    """
    choices = tuple(row for row in rows if can_launch(row, model))
    if not choices:
        capacity_summary = "; ".join(capacity_description(row) for row in rows)
        pytest.skip(f"harness {harness!r} has no available account: {capacity_summary}")
    return max(
        choices,
        key=lambda row: (
            -1 if row.scheduling_score is None else row.scheduling_score,
            row.default_for_launch,
        ),
    )


def can_launch(row: UsageRowResponse, model: str | None) -> bool:
    """Return whether an account has capacity for a model.

    Returns:
        ``True`` if the account can launch the model.

    """
    if row.authentication_error or not row.scheduling_allowed or row.limit:
        return False
    relevant = tuple(window for window in row.windows if window_matches_model(window, model))
    return bool(relevant) and all(window.used_percent < FULL_USAGE_PERCENT for window in relevant)


def window_matches_model(window: UsageWindowResponse, model: str | None) -> bool:
    """Return whether one usage window can run the model.

    Returns:
        ``True`` if the window applies to the model.

    """
    return window.model_id is None or model is None or window.model_id == model


def capacity_description(row: UsageRowResponse) -> str:
    """Describe the capacity status of one account.

    Returns:
        A concise capacity description.

    """
    identity = row.account_id or row.display_name
    if row.authentication_error:
        return f"{identity} authentication failed"
    if row.limit:
        return f"{identity} is blocked"
    if not row.windows:
        return f"{identity} usage is unavailable"
    return f"{identity} {window_usage_description(row.windows)}"


def window_usage_description(windows: tuple[UsageWindowResponse, ...]) -> str:
    """Describe the used capacity of account windows.

    Returns:
        A comma-separated window usage description.

    """
    return ", ".join(f"{window.key}={window.used_percent}%" for window in windows)
