# Copyright (c) 2026 Zhambyl Yermagambet
"""Map Web Push preference rows and SQL values."""

from __future__ import annotations

from domain.preferences import PushSigningKeypair, PushSubscription
from repository.model.preferences import PushSigningKeyRow, PushSubscriptionRow


def push_subscription(push_subscription_row: PushSubscriptionRow) -> PushSubscription:
    """Return a Push subscription from its row.

    Returns:
        A Push subscription from its row.

    """
    return PushSubscription(
        endpoint=push_subscription_row.endpoint,
        public_key=push_subscription_row.public_key,
        authentication_secret=push_subscription_row.authentication_secret,
        device_id=push_subscription_row.device_id,
        device_label=push_subscription_row.device_label,
        created_at=push_subscription_row.created_at,
    )


def push_subscription_row(push_subscription: PushSubscription) -> PushSubscriptionRow:
    """Return a row for a Push subscription.

    Returns:
        A row for a Push subscription.

    """
    return PushSubscriptionRow(
        endpoint=push_subscription.endpoint,
        public_key=push_subscription.public_key,
        authentication_secret=push_subscription.authentication_secret,
        device_id=push_subscription.device_id,
        device_label=push_subscription.device_label,
        created_at=push_subscription.created_at,
    )


def push_signing_keypair(push_signing_key_row: PushSigningKeyRow) -> PushSigningKeypair:
    """Return a Push signing key pair from its row.

    Returns:
        A Push signing key pair from its row.

    """
    return PushSigningKeypair(push_signing_key_row.private_key_pem, push_signing_key_row.public_key)
