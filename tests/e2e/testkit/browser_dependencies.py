# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide browser driver dependencies."""


from tests.e2e.testkit import (
    browser_client_dependencies as _client,
    browser_model_dependencies as _models,
    browser_runtime_dependencies as _runtime,
    browser_standard_dependencies as _standard,
    browser_terminal_dependencies as _terminal,
)

client = _client
models = _models
runtime = _runtime
standard = _standard
terminal = _terminal
