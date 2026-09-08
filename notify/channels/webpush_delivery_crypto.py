# Copyright (c) 2026 Zhambyl Yermagambet
"""Build encrypted Web Push request content."""

from __future__ import annotations

from typing import TYPE_CHECKING

from notify.channels.webpush_encryption import _encrypt
from notify.channels.webpush_vapid import _vapid_header

if TYPE_CHECKING:
    from repository.contract.preferences import PushSigningKeyRepository


def content_and_authorization(
    endpoint: str,
    content: bytes,
    browser_public_key: str,
    authentication_secret: str,
    push_signing_key_repository: PushSigningKeyRepository | None,
) -> tuple[bytes, str | None]:
    """Return encrypted content and its VAPID authorization.

    Returns:
        Encrypted content and authorization.

    """
    body = _encrypt(content, browser_public_key, authentication_secret)
    authorization = _vapid_header(endpoint, push_signing_key_repository)
    return body, authorization
