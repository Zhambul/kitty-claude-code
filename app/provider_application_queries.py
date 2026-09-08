# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide application-level session query services."""

from typing import Annotated

from fastapi import Depends

from app import (
    provider_audit_storage as audit_providers,
    provider_control_support as control_providers,
    provider_runtime as runtime_providers,
    provider_session_storage as session_providers,
)
from app.injection import singleton
from app.services import insight_resources, insights, resume
from dashboard import config as dashboard_config


@singleton
def application_insights(
    read_model: session_providers.SessionDataStore,
    terminal_input: control_providers.TerminalInput,
    audit_reader: audit_providers.AuditReads,
    checkouts: runtime_providers.Repositories,
) -> insights.ApplicationInsightsService:
    """Return the cross-session application insight service.

    Returns:
        Cross-session application insight service.

    """
    return insights.ApplicationInsightsService(
        insight_resources.ApplicationInsightResources(
            read_model,
            terminal_input,
            audit_reader,
            checkouts,
            dashboard_config.INSIGHTS_PROJECT_LIMIT,
        ),
    )


Insights = Annotated[
    insights.ApplicationInsightsService,
    Depends(application_insights),
]


@singleton
def resumable_sessions(
    read_model: session_providers.SessionDataStore,
    terminal_input: control_providers.TerminalInput,
    checkouts: runtime_providers.Repositories,
) -> resume.ResumableSessionService:
    """Return the session resume query service.

    Returns:
        Session resume query service.

    """
    return resume.ResumableSessionService(
        read_model,
        terminal_input,
        checkouts,
        result_limit=dashboard_config.RESUMABLE_SESSION_LIMIT,
    )


ResumableSessions = Annotated[
    resume.ResumableSessionService,
    Depends(resumable_sessions),
]
