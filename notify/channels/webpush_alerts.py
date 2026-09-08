# Copyright (c) 2026 Zhambyl Yermagambet
"""Own Web Push alerts."""

from __future__ import annotations

import threading
from typing import TYPE_CHECKING

from dashboard import config
from notify.channels.alert import NOTHING, OK, Alert, alert_text, push_tag
from notify.channels.webpush_availability import enabled
from notify.channels.webpush_fanout import _webpush_fanout
from notify.channels.webpush_payloads import (
    WebPushAlertPayload,
    WebPushHandle,
    WebPushResolvePayload,
    _WebPushAlertFields,
)

if TYPE_CHECKING:
    from notify.presence import RoutedSubscription
    from repository.contract.preferences import (
        PushSigningKeyRepository,
        PushSubscriptionRepository,
    )


def send_alert(
    alert: Alert,
    subs: list[RoutedSubscription],
    badge: int = 0,
    *,
    push_signing_key_repository: PushSigningKeyRepository | None = None,
    push_subscription_repository: PushSubscriptionRepository | None = None,
) -> WebPushHandle | None:
    """Send alert.

    Send the on-device alert as a Web Push to `subs` — the subscriptions of
        the ONE device the caller routed to (`presence.route`), NOT every
        subscription, so a session going done/asking buzzes the device you're
        working on, not your iPad and Mac at once. Dispatched on a detached daemon thread: the crypto +
        network round-trips must never stall the 1 s watcher. Best-effort + audited;
        a subscription the push service reports GONE (404/410) is pruned. No-op when
        the crypto backend is missing or `subs` is empty.

        The ROUTING is deliberately not decided here — a transport that picked its
        own destination could not be reused by the retraction, which must reach the
        devices the alert ACTUALLY went to rather than whichever is most-recently-
        used by then. The caller passes the targets and audits `notify-route`.

        Returns a handle (the alert is out on these subscriptions, and a resolve
        push can close it) or None — which the caller reads as "no device to push
        to", the signal that holds Telegram back to the escalation nudge.

    Returns:
        The web push handle.

    """
    if not (enabled() and subs):
        return None
    session_id = alert.session_id
    payload = _webpush_payload(alert, badge)
    threading.Thread(
        target=_webpush_fanout,
        args=(subs, payload, "send", push_signing_key_repository, push_subscription_repository),
        daemon=True,
    ).start()
    # The subscriptions are the handle: a resolve push has to reach the devices
    # the alert actually went to, NOT whichever device is most-recently-used by
    # then — the banner is on the former.
    return WebPushHandle(session_id=session_id, kind=alert.kind, subs=subs, tag=push_tag(session_id))


def _webpush_payload(alert: Alert, badge: int) -> WebPushAlertPayload:
    title, body, url = alert_text(alert)
    fields = _WebPushAlertFields(title, body, alert.session_id, alert.kind, url, badge)
    return WebPushAlertPayload.model_validate(fields, from_attributes=True)


def retract_alert(
    web_push_handle: WebPushHandle,
    badge: int = 0,
    *,
    push_signing_key_repository: PushSigningKeyRepository | None = None,
    push_subscription_repository: PushSubscriptionRepository | None = None,
) -> str:
    """Retract alert.

    Close the delivered banner by pushing a RESOLVE message to the same
        subscriptions; sw.js closes everything under the tag and shows nothing.

        That "shows nothing" is the load-bearing risk of this whole path: an iOS
        subscription is `userVisibleOnly`, and WebKit may answer a push that raises
        no notification with a generic placeholder banner — or, if it keeps
        happening, revoke the subscription. What keeps that survivable is the
        BUDGET: exactly one resolve per delivered alert (the notifier forgets the
        record either way), so the silent:visible ratio is bounded at 1:1 rather
        than being a background chatter channel. BAQYLAU_DASHBOARD_RESOLVE_PUSH=0 turns it
        off, and the page's own foreground sweep (push-notifications.ts) still clears
        stale banners on open — so a refused or dropped resolve degrades to "cleared
        a bit later", never to a wrong badge.

    Returns:
        Text result.

    """
    if not config.RESOLVE_PUSH:
        return NOTHING
    subs = web_push_handle.subs
    if not subs:
        return NOTHING
    payload = WebPushResolvePayload(
        session_id=web_push_handle.session_id,
        kind=web_push_handle.kind,
        tag=web_push_handle.tag,
        badge=badge,
    )
    threading.Thread(
        target=_webpush_fanout,
        args=(subs, payload, "resolve", push_signing_key_repository, push_subscription_repository),
        daemon=True,
    ).start()
    return OK  # dispatched; the thread audits the send
