# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide availability-aware one-shot inference."""

from __future__ import annotations

from typing import TYPE_CHECKING

from inference import providers, runner as model_runner, small as small_model
from inference.options import DefaultModelOptions
from inference.runner_resources import ModelRunnerResources

if TYPE_CHECKING:
    from audit.recorder import AuditRecorder
    from inference.contract import Model
    from terminal.contract import TerminalPlugin


class DefaultModelFactory:
    """Provide the default application models."""

    def __init__(
        self,
        terminal_plugin: TerminalPlugin,
        usage_reader: providers.UsageReader,
        audit_recorder: AuditRecorder,
        options: DefaultModelOptions | None = None,
    ) -> None:
        """Create a factory with terminal, usage, and audit services."""
        selected_options = options or DefaultModelOptions()
        self.terminal = terminal_plugin
        self.usage = usage_reader
        self.audit = audit_recorder
        self.runtime_configs = selected_options.resolved_runtime_configs()
        self.timeout_seconds = selected_options.timeout_seconds
        self.executable_resolver = selected_options.resolved_executable_resolver(
            self.runtime_configs,
        )

    def big(self) -> Model:
        """Report that a large default model is not configured."""
        raise NotImplementedError

    def mid(self) -> Model:
        """Report that a middle default model is not configured."""
        raise NotImplementedError

    def small(self) -> Model:
        """Return the configured small model.

        Returns:
            Configured small model.

        """
        selector = providers.ProviderSelector(
            self.usage,
            self.runtime_configs,
            self.executable_resolver,
        )
        runner = model_runner.ModelRunner(
            ModelRunnerResources(
                self.terminal,
                self.runtime_configs,
                self.timeout_seconds,
            ),
        )
        return small_model.SmallModel(selector, runner, self.audit)
