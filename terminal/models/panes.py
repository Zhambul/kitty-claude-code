# Copyright (c) 2026 Zhambyl Yermagambet
"""Pane operations — split, close, resize, focus."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum

from terminal.models.values import WindowId

MINIMUM_PANE_SIZE_PERCENT = 1
MAXIMUM_PANE_SIZE_PERCENT = 99


class SplitAxis(StrEnum):
    """Represent split axis."""

    VERTICAL = "vertical"
    HORIZONTAL = "horizontal"


@dataclass(frozen=True)
class PaneAnchor:
    """Where a split attaches, as INTENT rather than syntax.

    The caller states "next to that window" or "next to the pane tagged X"; the
    implementation renders its own match expression for it. Re-encoding the
    anchor as one terminal's match string above this
    layer would destroy the intent at the boundary — the caller's meaning could
    then only be recovered by parsing one terminal's grammar back apart.
    """

    window_id: WindowId | None = None
    tag: tuple[str, str] | None = None

    def __post_init__(self) -> None:
        """Validate the initialized object.

        Raises:
            ValueError: If an input value is not valid.

        """
        if (self.window_id is None) == (self.tag is None):
            message = "a pane anchor names exactly one of a window id or a tag"
            raise ValueError(message)


@dataclass(frozen=True)
class PaneOpenRequest:
    """A new pane running `command`, split off the anchor.

    `same_tab_as` is a window id whose TAB the pane must open in. It is not
    redundant with `anchor`: an anchor may only be resolvable within one tab,
    so the tab has to be selected first — otherwise a pane anchored to a window
    in an unfocused tab splits whichever tab the user happens to be looking at.
    """

    command: tuple[str, ...]
    working_directory: str
    title: str
    # The SPLIT LINE's orientation: "vertical" puts the new pane beside the
    # anchor, "horizontal" stacks it under the anchor.
    split: SplitAxis
    size_percent: int  # the new pane's share of the split axis
    anchor: PaneAnchor
    same_tab_as: str
    tags: Mapping[str, str]
    keep_focus: bool = True

    def __post_init__(self) -> None:
        """Validate the initialized object.

        Raises:
            ValueError: If an input value is not valid.

        """
        if not MINIMUM_PANE_SIZE_PERCENT <= self.size_percent <= MAXIMUM_PANE_SIZE_PERCENT:
            message = "pane size must be between 1 and 99 percent"
            raise ValueError(message)


@dataclass(frozen=True)
class PaneCloseRequest:
    """Represent pane close request."""

    window_id: WindowId


@dataclass(frozen=True)
class PaneResizeRequest:
    """Represent pane resize request."""

    window_id: WindowId
    axis: SplitAxis
    cells: int  # grow (+) / shrink (-)


@dataclass(frozen=True)
class WindowFocusRequest:
    """Focus a window INSIDE its tab.

    The move must not raise or activate the terminal's OS window: a focus that
    activates a background application steals the user's screen away from
    whatever they are actually looking at.
    """

    window_id: WindowId
