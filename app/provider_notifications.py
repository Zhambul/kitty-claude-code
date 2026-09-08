# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide application update, presence, and notification state."""

from typing import Annotated

from fastapi import Depends

from app.injection import singleton
from dashboard.services import application_updates, notices
from notify.presence import Presence


@singleton
def application_update_state() -> application_updates.ApplicationUpdateState:
    """Return the shared application update publisher.

    Returns:
        Shared application update publisher.

    """
    return application_updates.ApplicationUpdateState()


ApplicationUpdates = Annotated[
    application_updates.ApplicationUpdateState,
    Depends(application_update_state),
]


@singleton
def presence() -> Presence:
    """Return the shared dashboard presence state.

    Returns:
        Shared dashboard presence state.

    """
    return Presence()


PresenceSignals = Annotated[Presence, Depends(presence)]


@singleton
def dashboard_notification_state(
    updates: ApplicationUpdates,
) -> notices.DashboardNotificationState:
    """Return dashboard notification revision state.

    Returns:
        Dashboard notification revision state.

    """
    return notices.DashboardNotificationState(updates.publish)


NotificationState = Annotated[
    notices.DashboardNotificationState,
    Depends(dashboard_notification_state),
]
