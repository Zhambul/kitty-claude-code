# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide global application preference services."""

from typing import Annotated

from fastapi import Depends

from app import (
    application_preference_resources as resources,
    provider_harness_sessions as session_providers,
    provider_notifications as notification_providers,
    provider_preference_storage as storage_providers,
    provider_runtime as runtime_providers,
    provider_session_storage as session_data_providers,
    provider_terminal as terminal_providers,
    provider_usage as usage_providers,
)
from app.injection import singleton
from dashboard.services import preferences as preference_service


@singleton
def application_preference_core(
    read_model: session_data_providers.SessionDataStore,
    session_storage: session_providers.Sessions,
    adapter: terminal_providers.Terminal,
    checkouts: runtime_providers.Repositories,
    usage: usage_providers.UsageState,
) -> resources.ApplicationPreferenceCore:
    """Return live resources for global preferences.

    Returns:
        Live resources for global preferences.

    """
    return resources.ApplicationPreferenceCore(
        read_model,
        session_storage,
        adapter,
        checkouts,
        usage,
    )


ApplicationCore = Annotated[
    resources.ApplicationPreferenceCore,
    Depends(application_preference_core),
]


@singleton
def application_preference_settings(
    notices: notification_providers.NotificationState,
    drafts: storage_providers.NewSessions,
    settings: storage_providers.NotificationSettings,
    directories: storage_providers.HiddenDirectories,
    subscriptions: storage_providers.PushSubscriptions,
) -> resources.ApplicationPreferenceSettings:
    """Return stored resources for global preferences.

    Returns:
        Stored resources for global preferences.

    """
    return resources.ApplicationPreferenceSettings(
        notices,
        drafts,
        settings,
        directories,
        subscriptions,
    )


ApplicationSettings = Annotated[
    resources.ApplicationPreferenceSettings,
    Depends(application_preference_settings),
]


@singleton
def application_preference_signals(
    signals: notification_providers.PresenceSignals,
    updates: notification_providers.ApplicationUpdates,
) -> resources.ApplicationPreferenceSignals:
    """Return live signals for global preferences.

    Returns:
        Live signals for global preferences.

    """
    return resources.ApplicationPreferenceSignals(signals, updates)


ApplicationSignals = Annotated[
    resources.ApplicationPreferenceSignals,
    Depends(application_preference_signals),
]


@singleton
def application_preferences(
    core: ApplicationCore,
    settings: ApplicationSettings,
    signals: ApplicationSignals,
) -> preference_service.ApplicationPreferenceService:
    """Return the global application preference service.

    Returns:
        Global application preference service.

    """
    return preference_service.ApplicationPreferenceService(
        core,
        settings,
        signals,
    )


ApplicationPreferences = Annotated[
    preference_service.ApplicationPreferenceService,
    Depends(application_preferences),
]
