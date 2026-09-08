# Copyright (c) 2026 Zhambyl Yermagambet
"""Tab operations — open, close, rename, colour."""

from __future__ import annotations

from dataclasses import dataclass

from terminal.models.values import TabAppearance, WindowId


@dataclass(frozen=True)
class EnvironmentVariable:
    """One environment value for a terminal command."""

    name: str
    content: str


@dataclass(frozen=True)
class TabOpenRequest:
    """A new tab running `command` in `working_directory`.

    `environment` rides the launch: assignments the command needs that are
    facts of the launch itself (the selected account, model, effort), not of
    the daemon that requested it.
    """

    working_directory: str
    command: tuple[str, ...]
    # The tab's intended title. An implementation whose only way to set one is
    # a STICKY title leaves it to the program instead — a harness publishes its
    # own tab title, and freezing that out at launch loses more than it gains.
    # `TabRenameRequest` is the deliberate override.
    title: str
    environment: tuple[EnvironmentVariable, ...] = ()


@dataclass(frozen=True)
class TabCloseRequest:
    """Represent tab close request."""

    window_id: WindowId  # closes the whole tab CONTAINING this window


@dataclass(frozen=True)
class TabRenameRequest:
    """Represent tab rename request."""

    window_id: WindowId
    title: str  # a sticky, explicit title


@dataclass(frozen=True)
class TabColorSetRequest:
    """Represent tab color set request."""

    window_id: WindowId
    appearance: TabAppearance


@dataclass(frozen=True)
class TabColorClearRequest:
    """Represent tab color clear request."""

    window_id: WindowId
