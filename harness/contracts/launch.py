# Copyright (c) 2026 Zhambyl Yermagambet
"""Define harness launch, catalog, and usage contracts."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from harness.models.catalog import HarnessCatalogSnapshot, QueryContext
    from harness.models.launch import LaunchRequest, LaunchResult
    from harness.models.usage import UsageRow


class HarnessLauncher(Protocol):
    """Launch one harness session."""

    def launch(self, launch_request: LaunchRequest) -> LaunchResult:
        """Launch a session."""
        ...


class HarnessCatalog(Protocol):
    """Read the launch catalog for a harness."""

    def read(self, query_context: QueryContext) -> HarnessCatalogSnapshot:
        """Read the harness catalog."""
        ...


class HarnessUsage(Protocol):
    """Read current plan-limit rows for a harness."""

    def read(self) -> tuple[UsageRow, ...]:
        """Read current usage rows."""
        ...
