# Copyright (c) 2026 Zhambyl Yermagambet
"""Real harness journeys through Kitty and the dashboard API."""

from __future__ import annotations

import os

import pytest
from pytest_bdd import scenarios

from tests.e2e.testkit.policy import E2E_SCENARIO_TIMEOUT_SECONDS

pytestmark = [
    pytest.mark.drift,
    pytest.mark.kitty,
    pytest.mark.timeout(E2E_SCENARIO_TIMEOUT_SECONDS),
    pytest.mark.skipif(
        not os.environ.get("BAQYLAU_E2E_REAL_TERMINAL"),
        reason="real-terminal E2E tests are opt-in",
    ),
]

scenarios(
    "../features/background_restart.feature",
    "../features/terminal_mid_turn.feature",
    "../features/journeys.feature",
    "../features/draft_sync.feature",
    "../features/runtime_restart.feature",
    "../features/terminal.feature",
)
