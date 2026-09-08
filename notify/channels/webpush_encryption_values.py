# Copyright (c) 2026 Zhambyl Yermagambet
"""Own Web Push encryption values."""

from __future__ import annotations

RECORD_SIZE = 4096  # aes128gcm record size (rs) — our payloads are tiny


KEY_MATERIAL_BYTES = 32


SALT_BYTES = 16


CONTENT_KEY_BYTES = 16


NONCE_BYTES = 12
