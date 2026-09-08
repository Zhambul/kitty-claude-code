# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide e2e testkit dependencies."""

from tests.e2e.testkit import (
    session_contexts as session_contexts,
    terminal_models as terminal_models,
    terminals as _terminal_testkit,
)
from tests.e2e.testkit.work import WorkDriver as WorkDriver

terminal_testkit = _terminal_testkit
