# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide all session-data read routes."""

from fastapi import APIRouter

from api.sessiondata import entry_routes, list_routes, session_routes

router = APIRouter()
router.include_router(list_routes.router)
router.include_router(session_routes.router)
router.include_router(entry_routes.router)

session_data_list = list_routes.session_data_list
session_directories = list_routes.session_directories
session_data = session_routes.session_data
session_entries = entry_routes.session_entries
DEFAULT_ENTRY_LIMIT = entry_routes.DEFAULT_ENTRY_LIMIT
MAXIMUM_ENTRY_LIMIT = entry_routes.MAXIMUM_ENTRY_LIMIT
