# Copyright (c) 2026 Zhambyl Yermagambet
"""Collect routes that manage application preferences."""

from fastapi import APIRouter

from api.application import (
    preference_global_write_routes,
    preference_new_session_routes,
    preference_read_routes,
    preference_session_draft_routes,
    preference_session_read_routes,
    preference_session_view_routes,
)

router = APIRouter()
router.include_router(preference_read_routes.router)
router.include_router(preference_session_read_routes.router)

guarded = APIRouter()
guarded.include_router(preference_global_write_routes.router)
guarded.include_router(preference_new_session_routes.router)
guarded.include_router(preference_session_draft_routes.router)
guarded.include_router(preference_session_view_routes.router)
