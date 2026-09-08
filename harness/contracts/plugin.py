# Copyright (c) 2026 Zhambyl Yermagambet
"""Compose all capabilities of one harness plug-in."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from domain.references import ModelReference
from harness.contracts import (
    composer as composer_contracts,
    controller as controller_contracts,
    events,
    launch,
    reactor,
    sessions,
)
from harness.models.info import HarnessInfo


@dataclass(frozen=True)
class HarnessPlugin:
    """Compose the capabilities of one harness."""

    harness_info: HarnessInfo
    sources: events.HarnessRawEventSources
    translator: events.HarnessTranslator
    hooks: events.HarnessHookGateway | None = None
    telemetry: events.HarnessTelemetryGateway | None = None
    reactors: tuple[reactor.HarnessCanonicalEventReactor, ...] = ()
    controller: controller_contracts.HarnessController | None = None
    launcher: launch.HarnessLauncher | None = None
    catalog: launch.HarnessCatalog | None = None
    model_display: Callable[[ModelReference], str] | None = None
    usage: launch.HarnessUsage | None = None
    composer: composer_contracts.HarnessComposer | None = None
    resume_locator: sessions.HarnessResumeLocator | None = None
