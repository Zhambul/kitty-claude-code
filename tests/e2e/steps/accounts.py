# Copyright (c) 2026 Zhambyl Yermagambet
"""Real account selection actions and checks."""

from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING

from pytest_bdd import given, parsers, then

from tests.e2e.testkit import account_selection

if TYPE_CHECKING:
    from sdk.state import SessionSnapshot
    from tests.e2e.testkit.account_contexts import AccountSelectionContext, SessionAccountContext
    from tests.e2e.testkit.references import AccountSelectionRef


def _session_account_matches(
    snapshot: SessionSnapshot,
    expected: AccountSelectionRef,
) -> SessionSnapshot | None:
    account = snapshot.session_data.session.account
    if account is None:
        return None
    if account.account_id != expected.account_id or account.display_name != expected.display_name:
        message = (
            f"session account is {account.account_id!r} / {account.display_name!r}; "
            f"expected {expected.account_id!r} / {expected.display_name!r}"
        )
        raise AssertionError(message)
    return snapshot


@given(parsers.parse('session configuration "{session_name}" selects an available account "{account_name}"'))
def select_available_account(
    account_selection_context: AccountSelectionContext,
    session_name: str,
    account_name: str,
) -> None:
    """Process select available account."""
    account_selection.select_available(
        account_selection_context,
        session_name,
        account_name,
    )


@given(parsers.parse('session configuration "{session_name}" uses {mode} account'))
def configure_account_mode(
    account_selection_context: AccountSelectionContext,
    session_name: str,
    mode: str,
) -> None:
    """Process configure account mode."""
    if mode == "no":
        return
    if mode == "an available":
        account_selection.select_available(
            account_selection_context,
            session_name,
            f"{session_name} account",
        )
        return
    account_selection.select_by_id(
        account_selection_context,
        session_name,
        mode,
    )


@then(parsers.parse('session "{session_name}" uses account "{account_name}"'))
def session_uses_account(
    session_account_context: SessionAccountContext,
    session_name: str,
    account_name: str,
) -> None:
    """Process session uses account."""
    session = session_account_context.sessions.get(session_name)
    expected = session_account_context.account_selections.get(account_name)

    session_account_context.client.sessions.watch(session).wait(
        f"session {session_name!r} to report account {account_name!r}",
        partial(_session_account_matches, expected=expected),
        timeout=session_account_context.wait_policy.feed,
    )
