# Copyright (c) 2026 Zhambyl Yermagambet
"""Terminal value objects — colours, tab appearance, and the window entity.

Value objects and entities, not messages: they carry no Request/Response suffix
because they are what the operations are *about*, not the operations themselves.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import NewType

# Opaque terminal-side identities. Defined HERE rather than reused from
# `domain/ids.py`: `terminal/` may import nothing outside itself
# (test_the_terminal_contract_and_models_import_nothing_of_ours), so a second
# terminal stays implementable against this one small package. A caller that
# bridges a terminal window to a domain fact (`terminal/adapter.py`, the
# harness control modules) converts explicitly at that boundary.
WindowId = NewType("WindowId", str)
TabId = NewType("TabId", str)


# Generic window-metadata keys — baqylau's own names for "this window serves
# session X" / "this is the mirror pane" / "this is the scoreboard pane". Each
# terminal renders them in whatever per-window metadata it has; nothing above
# this layer knows that mechanism, or that one terminal calls it variables.
#
# The session key is a LIVENESS cross-check, not the session→window mapping:
# that mapping is a raw event (`Session.terminal_window_id`, kept current from the
# stored event of every hook-borne fact). The two pane keys are load-bearing: the
# mirror and scoreboard panes are daemon-created, so nothing else records them
# and the terminal must be able to find them again after a daemon restart.
SESSION_WINDOW_TAG = "baqylau_session"
ACTIVITY_PANE_TAG = "baqylau_activity"
SCOREBOARD_PANE_TAG = "baqylau_scoreboard"
RGB_COMPONENT_COUNT = 3


@dataclass(frozen=True)
class RGB:
    """Represent rgb."""

    red: int
    green: int
    blue: int

    @classmethod
    def from_hex(cls, hexadecimal: str) -> RGB:
        """Create a color from a six-digit hexadecimal value.

        Returns:
            The decoded color.

        Raises:
            ValueError: If the value does not contain three color bytes.

        """
        components = bytes.fromhex(hexadecimal.removeprefix("#"))
        if len(components) != RGB_COMPONENT_COUNT:
            message = "an RGB hexadecimal value must contain six digits"
            raise ValueError(message)
        return cls(components[0], components[1], components[2])

    def __post_init__(self) -> None:
        """Validate the initialized object.

        Raises:
            ValueError: If an input value is not valid.

        """
        maximum_component = 255
        for component in (self.red, self.green, self.blue):
            if component < 0 or component > maximum_component:
                message = "RGB components must be between 0 and 255"
                raise ValueError(message)


@dataclass(frozen=True)
class TabAppearance:
    """Represent tab appearance."""

    active_background: RGB
    active_foreground: RGB
    inactive_background: RGB
    inactive_foreground: RGB


@dataclass(frozen=True)
class WindowProcess:
    """One process that the terminal reports for a window."""

    process_id: int | None
    command: tuple[str, ...]


@dataclass(frozen=True)
class WindowInfo:
    """One window, as the terminal reports it.

    `is_first_in_tab` is creation order, which identifies the HOST pane: the
    session's own window is its tab's first window, and the mirror/scoreboard
    are split in after it. `tab_is_active` is "selected inside its OS window";
    `tab_is_focused` additionally requires that OS window to hold keyboard
    focus — a tab merely selected inside a BACKGROUNDED terminal (a session the
    web dashboard just spawned while you are on your phone) is active but not
    focused.
    """

    window_id: WindowId
    tab_id: TabId
    tags: Mapping[str, str]
    columns: int
    lines: int
    is_first_in_tab: bool
    tab_is_active: bool
    tab_is_focused: bool
    is_active_in_tab: bool = False
    processes: tuple[WindowProcess, ...] = ()
