# Copyright (c) 2026 Zhambyl Yermagambet
"""Retract delivered notifications."""

from pydantic import ValidationError

from audit import record as audit_record
from notify.audit import NotificationSessionAudit
from notify.channels.alert import FAILED, NOTHING
from notify.channels.telegram import TelegramHandle, retract_alert as retract_telegram_alert
from notify.channels.webpush import WebPushHandle, retract_alert as retract_webpush_alert
from repository.contract.preferences import (
    PushSigningKeyRepository,
    PushSubscriptionRepository,
)

type NotificationHandle = TelegramHandle | WebPushHandle


def _retract_notification(
    notification_handle: NotificationHandle,
    badge: int,
    push_signing_key_repository: PushSigningKeyRepository | None,
    push_subscription_repository: PushSubscriptionRepository | None,
) -> str:
    if isinstance(notification_handle, TelegramHandle):
        return retract_telegram_alert(notification_handle)
    return retract_webpush_alert(
        notification_handle,
        badge,
        push_signing_key_repository=push_signing_key_repository,
        push_subscription_repository=push_subscription_repository,
    )


def retract(
    notification_handle: NotificationHandle | None,
    badge: int = 0,
    *,
    push_signing_key_repository: PushSigningKeyRepository | None = None,
    push_subscription_repository: PushSubscriptionRepository | None = None,
) -> str:
    """Retract one delivered alert.

    Returns:
        The notification outcome.

    """
    if notification_handle is None:
        return NOTHING
    try:
        return _retract_notification(
            notification_handle,
            badge,
            push_signing_key_repository,
            push_subscription_repository,
        )
    except (RuntimeError, ValidationError):
        audit_record.error(
            "",
            "notify retract",
            NotificationSessionAudit(session_id=notification_handle.session_id),
        )
        return FAILED
