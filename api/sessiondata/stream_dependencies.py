# Copyright (c) 2026 Zhambyl Yermagambet
"""Build dependencies for session-data stream routes."""

from api.dependencies import Policy
from api.sessiondata.stream_global_models import GlobalFrameSources
from api.sessiondata.stream_session_models import SessionStreamServices
from app.provider_application_preferences import ApplicationPreferences
from app.provider_audit_storage import Recorder
from app.provider_notifications import ApplicationUpdates
from app.provider_session_application import SessionApplication
from app.provider_session_storage import SessionDataStore


def session_stream_services(
    read_model: SessionDataStore,
    audit: Recorder,
    session_application: SessionApplication,
    application_updates: ApplicationUpdates,
) -> SessionStreamServices:
    """Build the dependencies for one session stream.

    Returns:
        The services used by the session stream.

    """
    return SessionStreamServices(read_model, audit, session_application, application_updates.changes)


def global_stream_sources(
    read_model: SessionDataStore,
    audit: Recorder,
    policy: Policy,
    application_preferences: ApplicationPreferences,
    application_updates: ApplicationUpdates,
) -> GlobalFrameSources:
    """Build the dependencies for one global stream.

    Returns:
        The sources used by the global stream.

    """
    return GlobalFrameSources(read_model, audit, policy.boot_id, application_preferences, application_updates)
