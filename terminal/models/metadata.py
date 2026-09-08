# Copyright (c) 2026 Zhambyl Yermagambet
"""Window metadata operations — the write half of the window tag read."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from terminal.models.values import WindowId


@dataclass(frozen=True)
class WindowTagRequest:
    """Store metadata IN the window, so it has exactly the window's lifetime.

    A tag written here is never stale and survives a daemon restart — which is
    what the daemon-created mirror and scoreboard panes need to be found again.
    An empty value clears the tag.
    """

    window_id: WindowId
    tags: Mapping[str, str]


@dataclass(frozen=True)
class WindowTagResponse:
    """Represent window tag response."""

    succeeded: bool
    reason: str | None = None
