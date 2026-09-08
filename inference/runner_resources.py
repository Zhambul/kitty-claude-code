# Copyright (c) 2026 Zhambyl Yermagambet
"""Group the dependencies of one model provider runner."""

from __future__ import annotations

from dataclasses import dataclass

from harness.runtime import HarnessRuntimeConfigs
from terminal.contract import TerminalPlugin


@dataclass(frozen=True)
class ModelRunnerResources:
    """Hold terminal execution resources for a model runner."""

    terminal_plugin: TerminalPlugin
    runtime_configs: HarnessRuntimeConfigs
    timeout_seconds: float
