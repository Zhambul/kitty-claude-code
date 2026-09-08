# Copyright (c) 2026 Zhambyl Yermagambet
"""Own dashboard health values."""

HEALTH_PATH = "/api/health"


HEALTH_TIMEOUT_SECONDS = 1.0


PRIVATE_FILE_MODE = 0o600


STARTUP_ATTEMPTS = 40


STARTUP_POLL_SECONDS = 0.05


HEALTH_REQUEST_ERRORS = (OSError, ValueError, KeyError, TypeError)
