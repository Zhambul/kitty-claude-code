# Copyright (c) 2026 Zhambyl Yermagambet
"""Discover installed harness plugins."""

from __future__ import annotations

import importlib
from dataclasses import dataclass
from pathlib import Path

from audit.recorder import AuditRecorder
from domain.ids import HarnessName
from harness.contract import HarnessPlugin, SessionResumeRecorder
from harness.runtime import HarnessRuntimeConfigs, default_harness_runtime_configs
from terminal.contract import TerminalPlugin
from terminal.models.tabs import EnvironmentVariable


@dataclass(frozen=True)
class PluginBuildDependencies:
    """Group the dependencies shared by all discovered plug-ins."""

    runtime_configs: HarnessRuntimeConfigs
    terminal_plugin: TerminalPlugin | None
    session_resume_recorder: SessionResumeRecorder | None
    audit_recorder: AuditRecorder | None
    launch_environment: tuple[EnvironmentVariable, ...]


def installed(
    harness_runtime_configs: HarnessRuntimeConfigs | None = None,
    terminal_plugin: TerminalPlugin | None = None,
    session_resume_recorder: SessionResumeRecorder | None = None,
    audit_recorder: AuditRecorder | None = None,
    launch_environment: tuple[EnvironmentVariable, ...] = (),
) -> tuple[HarnessPlugin, ...]:
    """Return all harness plugins in directory order.

    Returns:
        Installed harness plugins.

    """
    dependencies = PluginBuildDependencies(
        harness_runtime_configs or default_harness_runtime_configs(),
        terminal_plugin,
        session_resume_recorder,
        audit_recorder,
        launch_environment,
    )
    return tuple(
        _installed_plugin(descriptor_path, dependencies)
        for descriptor_path in sorted(Path(__file__).resolve().parent.glob("*/plugin.py"))
    )


def _installed_plugin(
    descriptor_path: Path,
    plugin_build_dependencies: PluginBuildDependencies,
) -> HarnessPlugin:
    package_name = descriptor_path.parent.name
    module = importlib.import_module(f"harness.impl.{package_name}.plugin")
    factory = getattr(module, "build_plugin", None)
    descriptor = (
        factory(
            plugin_build_dependencies.runtime_configs.for_harness(HarnessName(package_name)),
            plugin_build_dependencies.terminal_plugin,
            plugin_build_dependencies.session_resume_recorder,
            plugin_build_dependencies.audit_recorder,
            plugin_build_dependencies.launch_environment,
        )
        if callable(factory)
        else None
    )
    if not isinstance(descriptor, HarnessPlugin):
        message = f"{module.__name__}.build_plugin must return a HarnessPlugin"
        raise TypeError(message)
    return descriptor
