# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide harness session storage and event gateways."""

from typing import Annotated

from fastapi import Depends

from app import (
    provider_databases as database_providers,
    provider_fact_storage as fact_providers,
    provider_harness_registry as registry_providers,
)
from app.injection import singleton
from harness.hooks import gateway as hook_gateway_service
from harness.services import telemetry
from repository.contract import sessions as session_contract
from repository.impl.sqlite import sessions as sqlite_sessions


@singleton
def sessions(
    database: database_providers.MainDb,
    harnesses: registry_providers.Registry,
) -> session_contract.SessionRepository:
    """Return harness-aware session storage.

    Returns:
        Harness-aware session storage.

    """
    return sqlite_sessions.SqliteSessionRepository(database, harnesses)


Sessions = Annotated[session_contract.SessionRepository, Depends(sessions)]


@singleton
def hook_gateway(
    harnesses: registry_providers.Registry,
    raw: fact_providers.RawEvents,
) -> hook_gateway_service.HookGatewayService:
    """Return the harness hook event gateway.

    Returns:
        Harness hook event gateway.

    """
    return hook_gateway_service.HookGatewayService(harnesses, raw)


HookGateway = Annotated[
    hook_gateway_service.HookGatewayService,
    Depends(hook_gateway),
]


@singleton
def telemetry_gateway(
    harnesses: registry_providers.Registry,
    raw: fact_providers.RawEvents,
    session_storage: Sessions,
) -> telemetry.TelemetryGatewayService:
    """Return the harness telemetry event gateway.

    Returns:
        Harness telemetry event gateway.

    """
    return telemetry.TelemetryGatewayService(harnesses, raw, session_storage)


TelemetryGateway = Annotated[
    telemetry.TelemetryGatewayService,
    Depends(telemetry_gateway),
]
