# Copyright (c) 2026 Zhambyl Yermagambet
"""Own Web Push availability."""

from __future__ import annotations

try:
    from notify.channels import webpush_crypto as _crypto_backend
except ImportError:  # pragma: no cover - optional dependency
    _CRYPTO_AVAILABLE = False
else:
    _CRYPTO_AVAILABLE = _crypto_backend.AESGCM is not None


def enabled() -> bool:
    """Return the enabled.

    Whether Web Push can be sent at all (the crypto backend is importable).
        False makes the whole feature invisible: `/api/push/config` reports it off
        and the Notifier never tries to send.

    Returns:
        Enabled.

    """
    return _CRYPTO_AVAILABLE
