# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide storage and effects used during harness launch."""

from typing import Annotated

from fastapi import Depends

from app import provider_databases as database_providers, provider_fact_storage as fact_providers
from app.injection import singleton
from harness.services import launch_effects
from repository.contract import sessions as session_contract
from repository.impl.sqlite import sessions as sqlite_sessions


@singleton
def launch_sessions(
    database: database_providers.MainDb,
) -> session_contract.SessionRepository:
    """Return session storage used while the harness registry starts.

    Returns:
        Session storage used while the harness registry starts.

    """
    return sqlite_sessions.SqliteSessionRepository(database)


LaunchSessions = Annotated[
    session_contract.SessionRepository,
    Depends(launch_sessions),
]


@singleton
def launch_effects_service(
    raw: fact_providers.RawEvents,
    session_storage: LaunchSessions,
) -> launch_effects.SessionLaunchEffectRecorder:
    """Return the harness launch effect recorder.

    Returns:
        Harness launch effect recorder.

    """
    return launch_effects.SessionLaunchEffectRecorder(raw, session_storage)


LaunchEffects = Annotated[
    launch_effects.SessionLaunchEffectRecorder,
    Depends(launch_effects_service),
]
