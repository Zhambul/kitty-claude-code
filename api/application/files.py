# Copyright (c) 2026 Zhambyl Yermagambet
"""Collect application routes that handle user files."""

from fastapi import APIRouter

from api.application import file_clipboard_route, file_dictation_route, file_upload_route

router = APIRouter()
router.include_router(file_upload_route.router)
router.include_router(file_clipboard_route.router)
router.include_router(file_dictation_route.router)
