# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide session aggregate writers and applied listeners."""

from typing import Annotated

from fastapi import Depends

from app import (
    provider_harness_registry as registry_providers,
    provider_harness_sessions as session_providers,
    provider_terminal as terminal_providers,
)
from app.injection import singleton
from engine.sessiondata import actors, contract, entries, naming, session
from terminal import tabs


@singleton
def model_naming(
    harness_registry: registry_providers.Registry,
) -> naming.ModelNaming:
    """Return model display names for each installed harness.

    Returns:
        Model display names for each installed harness.

    """
    display_by_harness = {
        plugin.harness_info.name: plugin.model_display
        for plugin in harness_registry.plugins()
        if plugin.model_display is not None
    }
    return naming.ModelNaming(display_by_harness)


Naming = Annotated[naming.ModelNaming, Depends(model_naming)]


@singleton
def entry_writer(model_names: Naming) -> contract.SessionEntryWriter:
    """Return the session entry writer.

    Returns:
        Session entry writer.

    """
    return entries.EntryWriter(model_names)


EntryWrites = Annotated[contract.SessionEntryWriter, Depends(entry_writer)]


@singleton
def session_data_writers(
    model_names: Naming,
) -> tuple[contract.SessionDataWriter, ...]:
    """Return session aggregate writers in fold order.

    Returns:
        Session aggregate writers in fold order.

    """
    writers = [
        session.SessionWriter(),
        session.GoalWriter(),
        session.TaskWriter(),
        actors.ActorWriter(model_names),
        actors.StatusWriter(),
        actors.UsageWriter(),
        actors.ContextWriter(),
        actors.StatisticsWriter(),
    ]
    return tuple(writers)


SessionDataWriters = Annotated[
    tuple[contract.SessionDataWriter, ...],
    Depends(session_data_writers),
]


@singleton
def applied_listeners(
    adapter: terminal_providers.Terminal,
    session_storage: session_providers.Sessions,
) -> tuple[contract.AppliedActorListener, ...]:
    """Return listeners for committed aggregate changes.

    Returns:
        Listeners for committed aggregate changes.

    """
    return (tabs.TabColorPainter(adapter, session_storage),)


AppliedListeners = Annotated[
    tuple[contract.AppliedActorListener, ...],
    Depends(applied_listeners),
]
