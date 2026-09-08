# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide browser operational telemetry."""

import os
from typing import Annotated

from fastapi import Depends

from app import provider_audit_storage as audit_providers
from app.injection import singleton
from audit import telemetry


@singleton
def browser_telemetry(
    writes: audit_providers.AuditWrites,
) -> telemetry.BrowserTelemetryService:
    """Return the browser telemetry service.

    Returns:
        Browser telemetry service.

    """
    return telemetry.BrowserTelemetryService(writes, os.getpid())


BrowserTelemetry = Annotated[
    telemetry.BrowserTelemetryService,
    Depends(browser_telemetry),
]
