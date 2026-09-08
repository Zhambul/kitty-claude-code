# Copyright (c) 2026 Zhambyl Yermagambet
"""Models for Claude Code shell output discovery."""

from __future__ import annotations

from dataclasses import dataclass

import bashlex  # type: ignore[import-untyped]


@dataclass(frozen=True)
class RedirectedOutput:
    """Represent redirected output."""

    path: str
    append: bool


@dataclass
class ShellDirectory:
    """Represent shell directory."""

    path: str
    known: bool = True

    def copy(self) -> ShellDirectory:
        """Return a separate shell directory state.

        Returns:
            A separate shell directory state.

        """
        return ShellDirectory(self.path, self.known)


@dataclass(frozen=True)
class ShellChild:
    """Pair one syntax node with its active directory."""

    node: bashlex.ast.node
    directory: ShellDirectory
