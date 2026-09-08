# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide grouped dependencies for committed-event reactions."""

from typing import Annotated

from fastapi import Depends

from app import (
    provider_auxiliary_storage as storage_providers,
    provider_control_support as support_providers,
    provider_harness_registry as registry_providers,
    provider_harness_sessions as session_providers,
    provider_session_storage as session_data_providers,
    provider_terminal as terminal_providers,
    reaction_resources,
)
from app.injection import singleton


@singleton
def reaction_terminal_resources(
    session_storage: session_providers.Sessions,
    adapter: terminal_providers.Terminal,
    widths: terminal_providers.PaneWidths,
    workspaces: session_data_providers.Workspaces,
) -> reaction_resources.ReactionTerminalResources:
    """Return terminal resources for committed-event reactions.

    Returns:
        Terminal resources for committed-event reactions.

    """
    return reaction_resources.ReactionTerminalResources(
        session_storage,
        adapter,
        widths,
        workspaces,
    )


ReactionTerminal = Annotated[
    reaction_resources.ReactionTerminalResources,
    Depends(reaction_terminal_resources),
]


@singleton
def reaction_control_resources(
    interrupts: support_providers.InterruptTracking,
    harnesses: registry_providers.Registry,
    jobs: storage_providers.NamingJobs,
    titles: terminal_providers.SessionTitles,
) -> reaction_resources.ReactionControlResources:
    """Return control resources for committed-event reactions.

    Returns:
        Control resources for committed-event reactions.

    """
    return reaction_resources.ReactionControlResources(
        interrupts,
        harnesses,
        jobs,
        titles,
    )


ReactionControl = Annotated[
    reaction_resources.ReactionControlResources,
    Depends(reaction_control_resources),
]
