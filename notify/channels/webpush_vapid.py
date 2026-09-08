# Copyright (c) 2026 Zhambyl Yermagambet
"""Own Web Push vapid."""

from __future__ import annotations

import dataclasses
import time
from typing import TYPE_CHECKING
from urllib.parse import urlparse

from notify.channels.webpush_crypto import decode_dss_signature, ec, hashes
from notify.channels.webpush_encoding import _b64u
from notify.channels.webpush_keys import _load_keypair
from notify.channels.webpush_vapid_models import ASCII_ENCODING, VapidClaims, VapidHeader
from notify.channels.webpush_vapid_values import SIGNATURE_COMPONENT_BYTES, TOKEN_LIFETIME_SECONDS, VAPID_SUB

if TYPE_CHECKING:
    from repository.contract.preferences import (
        PushSigningKeyRepository,
    )


@dataclasses.dataclass(frozen=True)
class _VapidSegments:
    header: str
    claims: str

    @property
    def signing_input(self) -> bytes:
        return f"{self.header}.{self.claims}".encode(ASCII_ENCODING)


def _vapid_header(endpoint: str, push_signing_key_repository: PushSigningKeyRepository | None) -> str | None:
    """Return the VAPID header.

    The `Authorization: vapid t=<jwt>, k=<pubkey>` header proving this server
        is the application server the subscription trusts (RFC 8292). The JWT's
        `aud` is the push service ORIGIN (scheme://host of the endpoint), signed
        ES256 with the VAPID private key — JOSE wants the raw r||s signature, so the
        DER the backend returns is unpacked here.

    Returns:
        VAPID header.

    """
    private_key, public_key_text = _load_keypair(push_signing_key_repository)
    if not private_key:
        return None
    token = _signed_vapid_token(endpoint, private_key)
    return f"vapid t={token}, k={public_key_text}"


def _signed_vapid_token(endpoint: str, private_key: ec.EllipticCurvePrivateKey) -> str:
    segments = _vapid_segments(endpoint)
    signature_der = private_key.sign(segments.signing_input, ec.ECDSA(hashes.SHA256()))
    signature = _raw_signature(signature_der)
    return f"{segments.header}.{segments.claims}.{_b64u(signature)}"


def _vapid_segments(endpoint: str) -> _VapidSegments:
    endpoint_parts = urlparse(endpoint)
    audience = f"{endpoint_parts.scheme}://{endpoint_parts.netloc}"
    header = _b64u(VapidHeader().model_dump_json().encode())
    claims = _b64u(
        VapidClaims(
            audience=audience,
            exp=int(time.time()) + TOKEN_LIFETIME_SECONDS,
            sub=VAPID_SUB,
        )
        .model_dump_json(by_alias=True)
        .encode(),
    )
    return _VapidSegments(header, claims)


def _raw_signature(signature_der: bytes) -> bytes:
    signature_first, signature_second = decode_dss_signature(signature_der)
    return signature_first.to_bytes(SIGNATURE_COMPONENT_BYTES, "big") + signature_second.to_bytes(
        SIGNATURE_COMPONENT_BYTES,
        "big",
    )
