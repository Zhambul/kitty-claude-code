# Copyright (c) 2026 Zhambyl Yermagambet
"""Expose the Web Push channel."""

from __future__ import annotations

from typing import TYPE_CHECKING

from notify.channels.webpush_alerts import retract_alert as retract_alert, send_alert as send_alert
from notify.channels.webpush_availability import enabled as enabled
from notify.channels.webpush_payloads import (
    WebPushAlertPayload as WebPushAlertPayload,
    WebPushHandle as WebPushHandle,
    WebPushPayload as WebPushPayload,
    WebPushResolvePayload as WebPushResolvePayload,
)

if TYPE_CHECKING:
    from repository.contract.preferences import PushSigningKeyRepository


def public_key(push_signing_key_repository: PushSigningKeyRepository) -> str:
    """Return the VAPID public key when crypto is available.

    Returns:
        VAPID public key.

    """
    if not enabled():
        return ""
    from notify.channels.webpush_keys import (  # noqa: PLC0415 -- Import keys after the optional crypto check.
        public_key as stored_public_key,
    )

    return stored_public_key(push_signing_key_repository)
