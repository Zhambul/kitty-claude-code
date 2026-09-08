# Copyright (c) 2026 Zhambyl Yermagambet
"""Own Web Push encoding."""

from __future__ import annotations

import base64

from notify.channels.webpush_vapid_models import ASCII_ENCODING


def _b64u(raw_bytes: bytes) -> str:
    """base64url without padding (the JOSE / RFC 8291 byte form).

    Returns:
        Text result.

    """
    return base64.urlsafe_b64encode(raw_bytes).rstrip(b"=").decode(ASCII_ENCODING)


def _b64u_dec(encoded_text: str) -> bytes:
    """Decode pad-stripped base64url (a subscription's p256dh/auth keys).

    Returns:
        Byte data.

    """
    encoded_text += "=" * (-len(encoded_text) % 4)
    return base64.urlsafe_b64decode(encoded_text.encode(ASCII_ENCODING))
