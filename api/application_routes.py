# Copyright (c) 2026 Zhambyl Yermagambet
"""Register application and control API routes."""

from fastapi import FastAPI

from api.application import catalog, files, preferences, static
from api.controls import routes as controls
from api.diagnostics import routes as diagnostics
from api.telemetry import browser as browser_telemetry


def configure(web: FastAPI) -> None:
    """Register control and application routes."""
    web.include_router(controls.router)
    web.include_router(diagnostics.router)
    web.include_router(preferences.router)
    web.include_router(preferences.guarded)
    web.include_router(browser_telemetry.router)
    web.include_router(files.router)
    web.include_router(catalog.router)
    web.include_router(static.router)
