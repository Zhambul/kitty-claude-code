# Copyright (c) 2026 Zhambyl Yermagambet
"""Results from tab commands."""

from __future__ import annotations

from dataclasses import dataclass

from terminal.models.values import WindowId


@dataclass(frozen=True)
class TabOpenResponse:
    """Report the result of a tab open command."""

    succeeded: bool
    window_id: WindowId | None
    reason: str | None = None


@dataclass(frozen=True)
class TabCloseResponse:
    """Report the result of a tab close command."""

    succeeded: bool
    reason: str | None = None


@dataclass(frozen=True)
class TabRenameResponse:
    """Report the result of a tab rename command."""

    succeeded: bool
    reason: str | None = None


@dataclass(frozen=True)
class TabColorSetResponse:
    """Report the result of a tab color command."""

    succeeded: bool
    reason: str | None = None


@dataclass(frozen=True)
class TabColorClearResponse:
    """Report the result of a tab color clear command."""

    succeeded: bool
    reason: str | None = None
