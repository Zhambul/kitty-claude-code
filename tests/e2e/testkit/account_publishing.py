# Copyright (c) 2026 Zhambyl Yermagambet
"""Wait predicates for published harness account rows."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from api.common.models.values.usage_row import UsageRowResponse
    from sdk.client import BaqylauClient


def configured_account(
    client: BaqylauClient,
    harness: str,
    account_id: str,
) -> UsageRowResponse | None:
    """Return the selected published account, if available.

    Returns:
        The selected row, or ``None`` when it is not published.

    Raises:
        AssertionError: If more than one matching row is published.

    """
    choices = [
        row
        for row in client.usage.state().usage_rows
        if row.harness == harness and row.account_id == account_id and row.switchable
    ]
    if len(choices) > 1:
        message = f"account {account_id!r} has {len(choices)} usage rows"
        raise AssertionError(message)
    return choices[0] if choices else None


def published_accounts(client: BaqylauClient, harness: str) -> tuple[UsageRowResponse, ...] | None:
    """Return switchable account rows after the harness publishes them.

    Returns:
        The rows, or ``None`` until they are available.

    """
    rows = switchable_rows(client, harness)
    return rows or None


def measured_accounts(client: BaqylauClient, harness: str) -> tuple[UsageRowResponse, ...] | None:
    """Return account rows once one row has capacity information.

    Returns:
        The rows, or ``None`` until capacity data is available.

    """
    rows = switchable_rows(client, harness)
    if not any(row.windows or row.limit or row.authentication_error for row in rows):
        return None
    return rows


def switchable_rows(client: BaqylauClient, harness: str) -> tuple[UsageRowResponse, ...]:
    """Return account rows that the harness permits a user to select.

    Returns:
        The switchable account rows.

    """
    return tuple(
        row
        for row in client.usage.state().usage_rows
        if row.harness == harness and row.switchable and row.account_id is not None
    )
