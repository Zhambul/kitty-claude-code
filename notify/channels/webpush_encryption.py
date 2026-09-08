# Copyright (c) 2026 Zhambyl Yermagambet
"""Own Web Push encryption."""

from __future__ import annotations

import dataclasses
import os
import struct

from notify.channels.webpush_crypto import AESGCM, HKDF, create_exchange, hashes
from notify.channels.webpush_encoding import _b64u_dec
from notify.channels.webpush_encryption_values import (
    CONTENT_KEY_BYTES,
    KEY_MATERIAL_BYTES,
    NONCE_BYTES,
    RECORD_SIZE,
    SALT_BYTES,
)


@dataclasses.dataclass(frozen=True)
class _PushExchange:
    browser_public: bytes
    server_public: bytes
    shared_secret: bytes


@dataclasses.dataclass(frozen=True)
class _ContentMaterial:
    salt: bytes
    content_key: bytes
    nonce: bytes


def _encrypt(payload: bytes, p256dh_b64u: str, auth_b64u: str) -> bytes:
    """Return the encrypt.

    Encrypt `payload` (bytes) for a subscription under the aes128gcm content
        encoding (RFC 8188) with the ECDH key agreement of RFC 8291. Returns the
        full message body (its own header carries the salt + our ephemeral public
        key, so the browser can derive the same key). Raises on bad key material —
        the caller audits + swallows.

    Returns:
        Encrypt.

    """
    exchange = _push_exchange(p256dh_b64u)
    material = _content_material(exchange, auth_b64u)
    ciphertext = _encrypt_content(payload, material)
    record_size = struct.pack("!L", RECORD_SIZE)
    public_size = bytes([len(exchange.server_public)])
    return material.salt + record_size + public_size + exchange.server_public + ciphertext


def _encrypt_content(payload: bytes, content_material: _ContentMaterial) -> bytes:
    """Return encrypted Web Push content.

    Returns:
        Encrypted Web Push content.

    """
    plaintext = b"".join((payload, b"\x02"))
    cipher = AESGCM(content_material.content_key)
    return cipher.encrypt(content_material.nonce, plaintext, None)


def _push_exchange(browser_public_text: str) -> _PushExchange:
    browser_public = _b64u_dec(browser_public_text)
    server_public, shared_secret = create_exchange(browser_public)
    return _PushExchange(browser_public, server_public, shared_secret)


def _content_material(push_exchange: _PushExchange, authentication_text: str) -> _ContentMaterial:
    authentication_secret = _b64u_dec(authentication_text)
    input_key_material = HKDF(
        algorithm=hashes.SHA256(),
        length=KEY_MATERIAL_BYTES,
        salt=authentication_secret,
        info=b"".join((b"WebPush: info\x00", push_exchange.browser_public, push_exchange.server_public)),
    ).derive(push_exchange.shared_secret)
    salt = os.urandom(SALT_BYTES)
    content_key = HKDF(
        algorithm=hashes.SHA256(),
        length=CONTENT_KEY_BYTES,
        salt=salt,
        info=b"Content-Encoding: aes128gcm\x00",
    ).derive(input_key_material)
    nonce = HKDF(
        algorithm=hashes.SHA256(),
        length=NONCE_BYTES,
        salt=salt,
        info=b"Content-Encoding: nonce\x00",
    ).derive(input_key_material)
    return _ContentMaterial(salt, content_key, nonce)
