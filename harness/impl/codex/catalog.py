# Copyright (c) 2026 Zhambyl Yermagambet
"""Codex menu vocabulary that depends on WHERE the session is."""

from __future__ import annotations

from harness.contract import HarnessCatalog
from harness.impl.codex import commands
from harness.models.catalog import (
    CommandOption,
    HarnessCatalogSnapshot,
    QueryContext,
)


class CodexCatalog(HarnessCatalog):
    """Represent codex catalog."""

    def __init__(self, configuration_directory: str) -> None:
        """Initialize the object."""
        self.configuration_directory = configuration_directory

    def read(self, query_context: QueryContext) -> HarnessCatalogSnapshot:
        """Return read.

        Returns:
            Read.

        """
        return HarnessCatalogSnapshot(
            commands=tuple(
                CommandOption(
                    command=row.name,
                    description=row.description,
                    minimum_prompt_count=0,
                )
                for row in commands.slash_commands(
                    query_context.working_directory or "",
                    self.configuration_directory,
                )
            ),
        )
