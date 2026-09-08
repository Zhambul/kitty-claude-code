# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide terminal adapters and pane services."""

from typing import Annotated

from fastapi import Depends

from app import (
    provider_audit_storage as audit_providers,
    provider_auxiliary_storage as storage_providers,
    provider_harness_sessions as session_providers,
    provider_runtime as runtime_providers,
)
from app.injection import singleton
from naming.renamer import SessionRenamer
from terminal import adapter as terminal_adapter
from terminal.panes import commands as pane_commands_service
from terminal.services import panes as pane_width_service_module


@singleton
def terminal(
    plugin: runtime_providers.InstalledTerminal,
    session_storage: session_providers.Sessions,
) -> terminal_adapter.TerminalAdapter:
    """Return the session-aware terminal adapter.

    Returns:
        Session-aware terminal adapter.

    """
    return terminal_adapter.TerminalAdapter(plugin, session_storage)


Terminal = Annotated[terminal_adapter.TerminalAdapter, Depends(terminal)]


@singleton
def session_renamer(adapter: Terminal) -> SessionRenamer:
    """Return the session title service.

    Returns:
        Session title service.

    """
    return SessionRenamer(adapter)


SessionTitles = Annotated[SessionRenamer, Depends(session_renamer)]


@singleton
def pane_width_service(
    widths: storage_providers.PaneWidthStorage,
) -> pane_width_service_module.PaneWidthService:
    """Return the pane-width service.

    Returns:
        Pane-width service.

    """
    return pane_width_service_module.PaneWidthService(widths)


PaneWidths = Annotated[
    pane_width_service_module.PaneWidthService,
    Depends(pane_width_service),
]


@singleton
def pane_commands(
    adapter: Terminal,
    pane_widths: PaneWidths,
    audit: audit_providers.Recorder,
) -> pane_commands_service.PaneCommandService:
    """Return terminal pane commands.

    Returns:
        Terminal pane commands.

    """
    return pane_commands_service.PaneCommandService(adapter, pane_widths, audit)


PaneCommands = Annotated[
    pane_commands_service.PaneCommandService,
    Depends(pane_commands),
]
