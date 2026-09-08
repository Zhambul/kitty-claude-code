# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide session read-model and workspace repositories."""

from typing import Annotated

from fastapi import Depends

from app import provider_databases as database_providers
from app.injection import singleton
from repository.contract import session_data as session_data_contract, workspace
from repository.impl.sqlite import session_data as sqlite_session_data, workspace as sqlite_workspace


@singleton
def session_data(
    database: database_providers.MainDb,
) -> session_data_contract.SessionDataRepository:
    """Return session read-model storage.

    Returns:
        Session read-model storage.

    """
    return sqlite_session_data.SqliteSessionDataRepository(database)


SessionDataStore = Annotated[
    session_data_contract.SessionDataRepository,
    Depends(session_data),
]


@singleton
def workspaces(
    database: database_providers.MainDb,
) -> workspace.SessionWorkspaceRepository:
    """Return session workspace storage.

    Returns:
        Session workspace storage.

    """
    return sqlite_workspace.SqliteSessionWorkspaceRepository(database)


Workspaces = Annotated[
    workspace.SessionWorkspaceRepository,
    Depends(workspaces),
]
