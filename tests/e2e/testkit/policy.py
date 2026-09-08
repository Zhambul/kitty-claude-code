# Copyright (c) 2026 Zhambyl Yermagambet
"""Runtime limits for live state changes, outside feature language."""

from dataclasses import dataclass

E2E_SCENARIO_TIMEOUT_SECONDS = 900


@dataclass(frozen=True)
class WaitPolicy:
    """Represent wait policy."""

    session_announcement: float = 300.0
    turn: float = 300.0
    feed: float = 120.0
    background: float = 120.0
    cleanup: float = 60.0
    pipeline: float = 30.0
