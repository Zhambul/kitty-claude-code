# Copyright (c) 2026 Zhambyl Yermagambet
"""What a harness's own TUI is showing right now, read off its screen."""

from __future__ import annotations

from dataclasses import dataclass

from domain.ids import WindowId


@dataclass(frozen=True)
class TerminalInputState:
    """Represent terminal input state."""

    typed_text: str | None
    suggestion: str | None


@dataclass(frozen=True)
class TerminalSessionState:
    """Represent terminal session state."""

    window_id: WindowId | None
    input_state: TerminalInputState | None
