# Copyright (c) 2026 Zhambyl Yermagambet
"""Claude Code menu vocabulary that depends on WHERE the session is."""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from harness.contract import HarnessCatalog
from harness.impl.claude_code import slashcmds
from harness.models.catalog import (
    CommandOption,
    HarnessCatalogSnapshot,
    QueryContext,
)

if TYPE_CHECKING:
    from collections.abc import Mapping

COMMAND_PROMPT_FLOORS: Mapping[str, int] = MappingProxyType({"compact": 2, "rename": 1})


def _minimum_prompt_count(command: str) -> int:
    return COMMAND_PROMPT_FLOORS.get(command, 0)


class ClaudeCodeCatalog(HarnessCatalog):
    """Represent claude code catalog."""

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
                    minimum_prompt_count=_minimum_prompt_count(row.name),
                )
                for row in slashcmds.slash_commands(
                    query_context.working_directory or "",
                    self.configuration_directory,
                )
            ),
        )
