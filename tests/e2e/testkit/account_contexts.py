# Copyright (c) 2026 Zhambyl Yermagambet
"""Contain focused dependencies for account BDD steps."""

from __future__ import annotations

from dataclasses import dataclass

from sdk.client import BaqylauClient
from tests.e2e.testkit.policy import WaitPolicy
from tests.e2e.testkit.references import (
    AccountSelections,
    Sessions,
    SessionSpecs,
)


@dataclass(frozen=True)
class AccountSelectionContext:
    """Contain services for session account selection."""

    client: BaqylauClient
    session_specs: SessionSpecs
    account_selections: AccountSelections
    wait_policy: WaitPolicy


@dataclass(frozen=True)
class SessionAccountContext:
    """Contain services for session account checks."""

    client: BaqylauClient
    sessions: Sessions
    account_selections: AccountSelections
    wait_policy: WaitPolicy
