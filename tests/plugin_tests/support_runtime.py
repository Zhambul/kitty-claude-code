# Copyright (c) 2026 Zhambyl Yermagambet
"""Shared fixtures and builders for canonical harness tests."""

from pathlib import Path

from engine.interpret.loop import Interpreter
from tests.canonical_runtime import CanonicalRuntime
from tests.plugin_tests.support_runtime_builders import harness_registry, interpreter


def interpreting_runtime(database_path: str | Path) -> tuple[CanonicalRuntime, Interpreter]:
    """Connect installed plugins to one test database and a silent terminal.

    Returns:
        The canonical storage runtime and its interpreter.

    """
    harnesses = harness_registry()
    runtime = CanonicalRuntime(str(database_path), harnesses=harnesses)
    return runtime, interpreter(runtime, harnesses)
