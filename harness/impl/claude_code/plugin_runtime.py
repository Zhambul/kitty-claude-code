# Copyright (c) 2026 Zhambyl Yermagambet
"""Build non-launch runtime components for the Claude Code plug-in."""

from harness.contract import HarnessPlugin
from harness.impl.claude_code import model_names
from harness.impl.claude_code.canonical import sources, translator
from harness.impl.claude_code.catalog import ClaudeCodeCatalog
from harness.impl.claude_code.controls.controller import controller
from harness.impl.claude_code.hooks.gateway import ClaudeHookGateway
from harness.impl.claude_code.otel.gateway import ClaudeTelemetryGateway
from harness.impl.claude_code.probe import ClaudeCodeComposer
from harness.impl.claude_code.reactors import ClaudeOtelCanonicalEventReactor
from harness.impl.claude_code.usage.rows import ClaudeCodeUsage
from harness.models.info import HarnessInfo
from harness.runtime import HarnessRuntimeConfig


def runtime_plugin(
    harness_runtime_config: HarnessRuntimeConfig,
    harness_info: HarnessInfo,
) -> HarnessPlugin:
    """Build a Claude Code plug-in without a launcher.

    Returns:
        The runtime plug-in.

    """
    configuration_directory = str(
        harness_runtime_config.configuration_directory,
    )
    return HarnessPlugin(
        harness_info=harness_info,
        hooks=ClaudeHookGateway(),
        telemetry=ClaudeTelemetryGateway(),
        sources=sources.ClaudeRawEventSources(configuration_directory),
        translator=translator.ClaudeCanonicalTranslator(),
        reactors=(ClaudeOtelCanonicalEventReactor(),),
        controller=controller,
        catalog=ClaudeCodeCatalog(configuration_directory),
        model_display=model_names.display_model,
        usage=ClaudeCodeUsage(harness_runtime_config),
        composer=ClaudeCodeComposer(),
    )
