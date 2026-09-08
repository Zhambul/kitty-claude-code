# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide preference repositories."""

from typing import Annotated

from fastapi import Depends

from app import provider_databases as database_providers
from app.injection import singleton
from repository.contract import preferences
from repository.impl.sqlite import preferences as sqlite_preferences


@singleton
def view_modes(database: database_providers.MainDb) -> preferences.ViewModeRepository:
    """Return session view-mode storage.

    Returns:
        Session view-mode storage.

    """
    return sqlite_preferences.SqliteViewModeRepository(database)


ViewModes = Annotated[preferences.ViewModeRepository, Depends(view_modes)]


@singleton
def notification_settings(
    database: database_providers.MainDb,
) -> preferences.NotificationSettingRepository:
    """Return notification setting storage.

    Returns:
        Notification setting storage.

    """
    return sqlite_preferences.SqliteNotificationSettingRepository(database)


NotificationSettings = Annotated[
    preferences.NotificationSettingRepository,
    Depends(notification_settings),
]


@singleton
def hidden_directories(
    database: database_providers.MainDb,
) -> preferences.HiddenDirectoryRepository:
    """Return hidden-directory storage.

    Returns:
        Hidden-directory storage.

    """
    return sqlite_preferences.SqliteHiddenDirectoryRepository(database)


HiddenDirectories = Annotated[
    preferences.HiddenDirectoryRepository,
    Depends(hidden_directories),
]


@singleton
def new_sessions(
    database: database_providers.MainDb,
) -> preferences.NewSessionRepository:
    """Return new-session draft storage.

    Returns:
        New-session draft storage.

    """
    return sqlite_preferences.SqliteNewSessionRepository(database)


NewSessions = Annotated[
    preferences.NewSessionRepository,
    Depends(new_sessions),
]


@singleton
def dismissals(
    database: database_providers.MainDb,
) -> preferences.TaskDismissalRepository:
    """Return task-dismissal storage.

    Returns:
        Task-dismissal storage.

    """
    return sqlite_preferences.SqliteTaskDismissalRepository(database)


Dismissals = Annotated[
    preferences.TaskDismissalRepository,
    Depends(dismissals),
]


@singleton
def push_subscriptions(
    database: database_providers.MainDb,
) -> preferences.PushSubscriptionRepository:
    """Return push-subscription storage.

    Returns:
        Push-subscription storage.

    """
    return sqlite_preferences.SqlitePushSubscriptionRepository(database)


PushSubscriptions = Annotated[
    preferences.PushSubscriptionRepository,
    Depends(push_subscriptions),
]


@singleton
def push_signing_keys(
    database: database_providers.MainDb,
) -> preferences.PushSigningKeyRepository:
    """Return push-signing-key storage.

    Returns:
        Push-signing-key storage.

    """
    return sqlite_preferences.SqlitePushSigningKeyRepository(database)


PushSigningKeys = Annotated[
    preferences.PushSigningKeyRepository,
    Depends(push_signing_keys),
]
