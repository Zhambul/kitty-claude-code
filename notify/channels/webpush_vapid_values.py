# Copyright (c) 2026 Zhambyl Yermagambet
"""Own Web Push vapid values."""

from __future__ import annotations

import os

VAPID_SUB = os.environ.get("BAQYLAU_DASHBOARD_VAPID_SUB") or "mailto:e.zhambul@gmail.com"


TOKEN_LIFETIME_SECONDS = 43_200  # VAPID token lifetime (Apple caps aud-JWTs at 24h)


SIGNATURE_COMPONENT_BYTES = 32
