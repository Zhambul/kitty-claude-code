# Copyright (c) 2026 Zhambyl Yermagambet
"""Own Web Push delivery."""

from __future__ import annotations

from http import HTTPStatus, client as http_client
from typing import TYPE_CHECKING
from urllib import error as urllib_error, request as urllib_request

from notify.channels.webpush_availability import enabled
from notify.channels.webpush_delivery_values import DELIVERY_LIFETIME_SECONDS
from notify.channels.webpush_vapid_models import PushErrorResponse

if TYPE_CHECKING:
    from notify.channels.webpush_payloads import WebPushPayload
    from notify.presence import RoutedSubscription
    from repository.contract.preferences import (
        PushSigningKeyRepository,
    )


class Result:
    """Represent result.

    A single send outcome the caller acts on: `ok` (delivered/accepted),
        `gone` (404/410 — the subscription is dead, prune it), else a soft failure
        (audited, kept — the push service may just be transiently unhappy).
    """

    __slots__ = ("error", "gone", "ok", "status")

    def __init__(
        self,
        *,
        ok: bool = False,
        gone: bool = False,
        status: int = 0,
        error: str = "",
    ) -> None:
        """Initialize the object."""
        self.ok = ok
        self.gone = gone
        self.status = status
        self.error = error


def deliver(
    routed_subscription: RoutedSubscription,
    payload: WebPushPayload,
    push_signing_key_repository: PushSigningKeyRepository | None,
    ttl: int = DELIVERY_LIFETIME_SECONDS,
) -> Result:
    """Deliver.

    Deliver `payload`, JSON-encoded, to one `subscription` (its JSON
        document: {endpoint, keys:{p256dh, auth}}). Never raises — returns a Result.
        Synchronous network I/O, so callers run it OFF the watcher thread.

    Returns:
        The result.

    """
    if not enabled():
        return Result(error="no crypto")
    try:
        return _send_delivery(routed_subscription, payload, push_signing_key_repository, ttl)
    except urllib_error.HTTPError as error:
        return _delivery_error(error)
    except Exception as error:  # noqa: BLE001 — the raised-path assertion
        return Result(error=str(error))


def _send_delivery(
    routed_subscription: RoutedSubscription,
    payload: WebPushPayload,
    push_signing_key_repository: PushSigningKeyRepository | None,
    ttl: int,
) -> Result:
    request = _delivery_request(routed_subscription, payload, push_signing_key_repository, ttl)
    if isinstance(request, Result):
        return request
    with urllib_request.urlopen(request, timeout=10) as response:  # noqa: S310 -- The request builder accepts only HTTPS endpoints.
        return Result(ok=True, status=response.status)


def _delivery_request(
    routed_subscription: RoutedSubscription,
    payload: WebPushPayload,
    push_signing_key_repository: PushSigningKeyRepository | None,
    ttl: int,
) -> urllib_request.Request | Result:
    from notify.channels.webpush_delivery_crypto import (  # noqa: PLC0415 -- Delivery checks the optional crypto backend before this call.
        content_and_authorization,
    )

    endpoint = routed_subscription["endpoint"]
    if not endpoint.startswith("https://"):
        return Result(error="push endpoint must use https")
    subscription_keys = routed_subscription["keys"]
    body, authorization = content_and_authorization(
        endpoint,
        payload.model_dump_json().encode("utf-8"),
        subscription_keys["p256dh"],
        subscription_keys["auth"],
        push_signing_key_repository,
    )
    if not authorization:
        return Result(error="no vapid")
    request_headers = {
        "Content-Encoding": "aes128gcm",
        "Content-Type": "application/octet-stream",
        "TTL": str(ttl),
        "Urgency": "high",
        "Authorization": authorization,
    }
    return urllib_request.Request(endpoint, data=body, method="POST", headers=request_headers)  # noqa: S310 -- The endpoint passed the HTTPS check above.


def _delivery_error(error: urllib_error.HTTPError) -> Result:
    try:
        response_reason = _push_error_reason(error)
    except (OSError, ValueError, http_client.HTTPException):
        response_reason = ""
    gone = error.code in {HTTPStatus.NOT_FOUND, HTTPStatus.GONE} or (
        error.code == HTTPStatus.BAD_REQUEST and response_reason == "VapidPkHashMismatch"
    )
    return Result(gone=gone, status=error.code, error=response_reason or str(error))


def _push_error_reason(error: urllib_error.HTTPError) -> str:
    response_body = error.read().decode("utf-8", "replace")
    return PushErrorResponse.model_validate_json(response_body).reason or ""
