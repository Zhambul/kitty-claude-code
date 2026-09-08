# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide canonical fact and shell-output repositories."""

from typing import Annotated

from fastapi import Depends

from app import provider_databases as database_providers
from app.injection import singleton
from repository.contract import facts, shell_output as shell_output_contract
from repository.impl.sqlite import (
    canonical_events as sqlite_canonical_events,
    raw_events as sqlite_raw_events,
    shell_output as sqlite_shell_output,
)


@singleton
def canonical_events(
    database: database_providers.MainDb,
) -> facts.CanonicalEventRepository:
    """Return canonical event storage.

    Returns:
        Canonical event storage.

    """
    return sqlite_canonical_events.SqliteCanonicalEventRepository(database)


CanonicalEvents = Annotated[
    facts.CanonicalEventRepository,
    Depends(canonical_events),
]


@singleton
def raw_events(database: database_providers.MainDb) -> facts.RawEventRepository:
    """Return raw event storage.

    Returns:
        Raw event storage.

    """
    return sqlite_raw_events.SqliteRawEventRepository(database)


RawEvents = Annotated[facts.RawEventRepository, Depends(raw_events)]


@singleton
def shell_output(
    database: database_providers.MainDb,
) -> shell_output_contract.ShellOutputRepository:
    """Return followed shell-output storage.

    Returns:
        Followed shell-output storage.

    """
    return sqlite_shell_output.SqliteShellOutputRepository(database)


ShellOutput = Annotated[
    shell_output_contract.ShellOutputRepository,
    Depends(shell_output),
]
