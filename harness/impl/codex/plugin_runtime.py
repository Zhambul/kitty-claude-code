# Copyright (c) 2026 Zhambyl Yermagambet
"""Build non-launch runtime components for the Codex plug-in."""

from harness.contract import HarnessPlugin
from harness.impl.codex.canonical.sources import CodexRawEventSources
from harness.impl.codex.canonical.title import CodexThreadTitleRepository
from harness.impl.codex.canonical.translator import CodexCanonicalTranslator
from harness.impl.codex.catalog import CodexCatalog
from harness.impl.codex.controls.composer import CodexComposer
from harness.impl.codex.controls.controller import build_controller, rewind_continuity
from harness.impl.codex.hooks.gateway import CodexHookGateway
from harness.impl.codex.resume import CodexResumeLocator
from harness.impl.codex.usage_rows import CodexUsage
from harness.models.info import HarnessInfo
from harness.runtime import HarnessRuntimeConfig


def runtime_plugin(
    harness_runtime_config: HarnessRuntimeConfig,
    harness_info: HarnessInfo,
) -> HarnessPlugin:
    """Build a Codex plug-in without a launcher.

    Returns:
        The runtime plug-in.

    """
    configuration_directory = str(
        harness_runtime_config.configuration_directory,
    )
    title_repository = CodexThreadTitleRepository(configuration_directory)
    return HarnessPlugin(
        harness_info=harness_info,
        hooks=CodexHookGateway(),
        sources=CodexRawEventSources(configuration_directory, title_repository),
        translator=CodexCanonicalTranslator(rewind_continuity),
        controller=build_controller(title_repository, harness_runtime_config),
        catalog=CodexCatalog(configuration_directory),
        usage=CodexUsage(harness_runtime_config),
        resume_locator=CodexResumeLocator(),
        composer=CodexComposer(),
    )
