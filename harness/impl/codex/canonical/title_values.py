# Copyright (c) 2026 Zhambyl Yermagambet
"""Values used by the Codex native title store."""

from __future__ import annotations

from dataclasses import dataclass

from domain.work_state import TitleOrigin


@dataclass(frozen=True)
class CodexNativeTitle:
    """Represent one native Codex title."""

    text: str
    origin: TitleOrigin


@dataclass(frozen=True)
class CodexTitleStoreMarker:
    """Describe native index files that can change a thread title."""

    database: str
    database_state: tuple[int, int, int]
    write_ahead_state: tuple[int, int, int] | None


@dataclass(frozen=True)
class ThreadTitleFields:
    """Hold the manual and generated title fields of one thread."""

    name: str
    automatic: str
