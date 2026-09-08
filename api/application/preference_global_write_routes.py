# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide global application preference write routes."""

from fastapi import APIRouter

from api.application.models.preferences.global_notifications_request import GlobalNotificationsRequest
from api.application.models.preferences.hidden_directories_response import HiddenDirectoriesResponse
from api.application.models.preferences.hide_directory_request import HideDirectoryRequest
from api.application.models.preferences.presence_request import PresenceRequest
from api.application.models.preferences.push_subscription_request import PushSubscriptionRequest
from api.common.models.replies.saved_response import SavedResponse
from app.provider_application_preferences import ApplicationPreferences
from dashboard.services.preference_models import BrowserPresence, BrowserPushSubscription
from domain.ids import DeviceId, SessionId

router = APIRouter()


@router.post("/api/application/notifications")
def set_global_notifications(
    global_notifications_request: GlobalNotificationsRequest,
    application_preferences: ApplicationPreferences,
) -> SavedResponse:
    """Set global notifications.

    Returns:
        The saved response.

    """
    application_preferences.set_notifications_enabled(enabled=global_notifications_request.enabled)
    return SavedResponse()


@router.post("/api/application/hidden-directories")
def hide_directory(
    hide_directory_request: HideDirectoryRequest,
    application_preferences: ApplicationPreferences,
) -> HiddenDirectoriesResponse:
    """Hide one project directory.

    Returns:
        The hidden directory response.

    """
    hidden = application_preferences.hide_directory(hide_directory_request.working_directory)
    return HiddenDirectoriesResponse(hidden=hidden)


@router.post("/api/application/push-subscriptions")
def register_push_subscription(
    push_subscription_request: PushSubscriptionRequest,
    application_preferences: ApplicationPreferences,
) -> SavedResponse:
    """Register a browser push subscription.

    Returns:
        The saved response.

    """
    subscription = push_subscription_request.subscription
    application_preferences.register_push_subscription(
        BrowserPushSubscription(
            subscription.endpoint,
            subscription.keys.p256dh,
            subscription.keys.auth,
            DeviceId(push_subscription_request.device_id),
            push_subscription_request.device_label or None,
        ),
    )
    return SavedResponse()


@router.post("/api/application/presence")
def report_presence(
    presence_request: PresenceRequest,
    application_preferences: ApplicationPreferences,
) -> SavedResponse:
    """Record browser presence.

    Returns:
        The saved response.

    """
    session_id = SessionId(presence_request.session_id) if presence_request.session_id else None
    application_preferences.report_presence(
        BrowserPresence(DeviceId(presence_request.device_id), session_id, presence_request.away),
    )
    return SavedResponse()
