# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide pane, naming-job, and upload repositories."""

from typing import Annotated

from fastapi import Depends

from app import provider_databases as database_providers
from app.injection import singleton
from repository.contract import naming, terminal, uploads
from repository.impl.sqlite import naming as sqlite_naming, terminal as sqlite_terminal, uploads as sqlite_uploads


@singleton
def pane_width_storage(
    database: database_providers.MainDb,
) -> terminal.PaneWidthRepository:
    """Return pane-width storage.

    Returns:
        Pane-width storage.

    """
    return sqlite_terminal.SqlitePaneWidthRepository(database)


PaneWidthStorage = Annotated[
    terminal.PaneWidthRepository,
    Depends(pane_width_storage),
]


@singleton
def naming_jobs(
    database: database_providers.MainDb,
) -> naming.NamingJobRepository:
    """Return automatic naming-job storage.

    Returns:
        Automatic naming-job storage.

    """
    return sqlite_naming.SqliteNamingJobRepository(database)


NamingJobs = Annotated[naming.NamingJobRepository, Depends(naming_jobs)]


@singleton
def upload_storage(
    database: database_providers.MainDb,
) -> uploads.UploadRepository:
    """Return staged-upload storage.

    Returns:
        Staged-upload storage.

    """
    return sqlite_uploads.SqliteUploadRepository(database)


UploadStorage = Annotated[uploads.UploadRepository, Depends(upload_storage)]
