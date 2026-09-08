# Copyright (c) 2026 Zhambyl Yermagambet
"""Own Web Push keys."""

from __future__ import annotations

from typing import TYPE_CHECKING

from cryptography.exceptions import UnsupportedAlgorithm

from audit import record as audit_record
from audit.documents import EmptyAudit
from domain.preferences import PushSigningKeypair
from notify.channels.webpush_availability import enabled
from notify.channels.webpush_crypto import create_keypair_material, ec, load_private_key
from notify.channels.webpush_encoding import _b64u
from notify.channels.webpush_vapid_models import ASCII_ENCODING

if TYPE_CHECKING:
    from repository.contract.preferences import (
        PushSigningKeyRepository,
    )


def _stored_private_key(
    push_signing_keypair: PushSigningKeypair,
) -> ec.EllipticCurvePrivateKey:
    return load_private_key(push_signing_keypair.private_key_pem.encode(ASCII_ENCODING))


def _load_keypair(
    push_signing_key_repository: PushSigningKeyRepository | None,
) -> tuple[ec.EllipticCurvePrivateKey | None, str | None]:
    """Load keypair.

    The persisted VAPID keypair as (private_key_obj, public_b64u), generated
        and stored on first use. One P-256 keypair per machine, stable across
        restarts so already-subscribed browsers keep matching — a rotated key would
        silently orphan every existing subscription. Returns (None, None) if crypto
        is unavailable / the store is unwritable (feature degrades off).

    Returns:
        Result items.

    """
    if not enabled() or push_signing_key_repository is None:
        return None, None
    stored = push_signing_key_repository.keypair()
    restored_keypair = _restore_keypair(stored)
    if restored_keypair is not None:
        return restored_keypair
    return _generate_keypair(push_signing_key_repository)


def _restore_keypair(
    push_signing_keypair: PushSigningKeypair | None,
) -> tuple[ec.EllipticCurvePrivateKey, str] | None:
    if push_signing_keypair is None:
        return None
    try:
        private_key = _stored_private_key(push_signing_keypair)
    except (TypeError, ValueError, UnsupportedAlgorithm):
        audit_record.error(
            "",
            "webpush keypair (corrupt record — regenerating)",
            EmptyAudit(),
        )
        return None
    return private_key, push_signing_keypair.public_key


def _generate_keypair(
    push_signing_key_repository: PushSigningKeyRepository,
) -> tuple[ec.EllipticCurvePrivateKey | None, str | None]:
    try:
        private_key, public_text = _create_keypair(push_signing_key_repository)
    except Exception:  # noqa: BLE001 -- Record key generation or storage failures and disable push.
        audit_record.error("", "webpush keygen")
        return None, None
    return private_key, public_text


def _create_keypair(push_signing_key_repository: PushSigningKeyRepository) -> tuple[ec.EllipticCurvePrivateKey, str]:
    private_key, public_point, private_pem = create_keypair_material()
    public_text = _b64u(public_point)
    private_text = private_pem.decode(ASCII_ENCODING)
    push_signing_key_repository.save_keypair(PushSigningKeypair(private_text, public_text))
    return private_key, public_text


def public_key(push_signing_key_repository: PushSigningKeyRepository) -> str:
    """Return the public key.

    The VAPID public key (base64url uncompressed point) the browser passes as
        `applicationServerKey` when it subscribes — '' when the feature is off.

    Returns:
        Public key.

    """
    _, pub = _load_keypair(push_signing_key_repository)
    return pub or ""
