# Copyright (c) 2026 Zhambyl Yermagambet
"""Real browser journeys against the live harness application."""

from __future__ import annotations

import os

import pytest
from pytest_bdd import scenarios

from tests.e2e.testkit.policy import E2E_SCENARIO_TIMEOUT_SECONDS

pytestmark = [
    pytest.mark.browser,
    pytest.mark.drift,
    pytest.mark.timeout(E2E_SCENARIO_TIMEOUT_SECONDS),
    pytest.mark.skipif(
        not os.environ.get("BAQYLAU_E2E_BROWSER"),
        reason="real-browser E2E tests are opt-in",
    ),
]

scenarios("../features/browser.feature")
