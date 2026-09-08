# Copyright (c) 2026 Zhambyl Yermagambet
"""Own Web Push fanout."""

from __future__ import annotations

from typing import TYPE_CHECKING

from audit import record as audit_record
from notify.audit import NotificationSessionAudit
from notify.channel_audit import WebPushAudit
from notify.channels.webpush_delivery import deliver
from notify.channels.webpush_delivery_values import AUDIT_ENDPOINT_CHARACTER_LIMIT

if TYPE_CHECKING:
    from notify.channels.webpush_payloads import (
        WebPushPayload,
    )
    from notify.presence import RoutedSubscription
    from repository.contract.preferences import (
        PushSigningKeyRepository,
        PushSubscriptionRepository,
    )


def _webpush_fanout(
    subs: list[RoutedSubscription],
    payload: WebPushPayload,
    action: str,
    push_signing_key_repository: PushSigningKeyRepository | None,
    push_subscription_repository: PushSubscriptionRepository | None,
) -> None:
    """Return the webpush fanout.

    The detached fan-out body, shared by the alert and its retraction:
        deliver `payload` to each subscription, audit the outcome (with the target
        `device` — the on-device analog of the route decision), and prune the dead
        ones. Runs off the watcher thread; never raises.
    """
    for sub in subs:
        try:
            res = deliver(sub, payload, push_signing_key_repository)
        except Exception:  # noqa: BLE001 -- Audit one failed delivery and continue with other subscriptions.
            audit_record.error(
                "",
                f"dashboard webpush {action}",
                NotificationSessionAudit(session_id=payload.session_id),
            )
            continue
        ep = sub["endpoint"]
        dev = sub["device"]
        if res.gone and push_subscription_repository is not None:
            push_subscription_repository.remove(ep)
        audit_record.state_file(
            "",
            "",
            "web-push",
            WebPushAudit(
                session_id=payload.session_id,
                kind=payload.kind,
                action=action,
                status=res.status,
                ok=res.ok,
                gone=res.gone,
                error=res.error,
                badge=payload.badge,
                device=dev,
                endpoint=ep[:AUDIT_ENDPOINT_CHARACTER_LIMIT],
            ),
        )
