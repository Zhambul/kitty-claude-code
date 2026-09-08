# Copyright (c) 2026 Zhambyl Yermagambet
"""The menu vocabulary one harness offers where a session is."""

from __future__ import annotations

from typing import TYPE_CHECKING

from domain.errors import UnsupportedRequestError

if TYPE_CHECKING:
    from domain.ids import HarnessName
    from harness.models.catalog import (
        HarnessCatalogSnapshot,
        QueryContext,
    )
    from harness.registry import HarnessRegistry


class HarnessCatalogService:
    """Represent harness catalog service."""

    def __init__(self, harness_registry: HarnessRegistry) -> None:
        """Initialize the object."""
        self.registry = harness_registry

    def read(self, harness: HarnessName, query_context: QueryContext) -> HarnessCatalogSnapshot:
        """Return read.

        Returns:
            Read.

        Raises:
            UnsupportedRequestError: If the control request is not supported.

        """
        catalog = self.registry.plugin(harness).catalog
        if catalog is None:
            # Installed, but it offers no menu — the request is the caller's to
            # fix, so it is typed rather than a bare ValueError.
            message = f"harness {harness!r} has no catalog"
            raise UnsupportedRequestError(message)
        return catalog.read(query_context)
