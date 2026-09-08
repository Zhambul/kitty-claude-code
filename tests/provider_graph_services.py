# Copyright (c) 2026 Zhambyl Yermagambet
"""Provider graph access to runtime services."""

from __future__ import annotations

from engine.react.loop import ReactionLoop
from harness.registry import HarnessRegistry
from harness.services.catalog import HarnessCatalogService
from harness.services.controls import HarnessControlService
from tests.provider_graph_context import ProviderGraphContext


class ProviderGraphServices(ProviderGraphContext):
    """Provide runtime service access."""

    @property
    def registry(self) -> HarnessRegistry:
        """The harness registry."""
        return self.provider("registry", HarnessRegistry)

    @property
    def reaction_loop(self) -> ReactionLoop:
        """The reaction loop."""
        return self.provider("reaction_loop", ReactionLoop)

    @property
    def catalog(self) -> HarnessCatalogService:
        """The harness catalog service."""
        return self.provider("catalog", HarnessCatalogService)

    @property
    def controls(self) -> HarnessControlService:
        """The harness control service."""
        return self.provider("controls", HarnessControlService)
