# Copyright (c) 2026 Zhambyl Yermagambet
"""The installed-daemon suite must not start an isolated test daemon."""

import pytest


@pytest.fixture(autouse=True)
def scenario_signoff() -> None:
    """Keep the installed daemon active after each test."""
