# Copyright (c) 2026 Zhambyl Yermagambet
"""Register observation API routes."""

from fastapi import FastAPI

from api.common import health
from api.hooks import routes as hooks
from api.sessiondata import routes as session_data_routes, streams as session_data_streams
from api.telemetry import harness as harness_telemetry
from api.terminal import panes


def configure(web: FastAPI) -> None:
    """Register health, input, and read routes."""
    web.include_router(health.router)
    web.include_router(hooks.router)
    web.include_router(harness_telemetry.router)
    web.include_router(panes.router)
    web.include_router(session_data_streams.router)
    web.include_router(session_data_routes.router)
