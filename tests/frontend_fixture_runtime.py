# Copyright (c) 2026 Zhambyl Yermagambet
"""Runtime dependencies for the frontend fixture seed."""

from app import (
    provider_fact_storage as provider_fact_storage,
    provider_harness_sessions as provider_harness_sessions,
    provider_reaction_loop as provider_reaction_loop,
    provider_runtime as provider_runtime,
    provider_session_storage as provider_session_storage,
)
from app.injection import registry as registry, resolve as resolve
from terminal.models.values import SESSION_WINDOW_TAG as SESSION_WINDOW_TAG
from tests.fake_terminal import FakeTerminal as FakeTerminal, window as window
