# Copyright (c) 2026 Zhambyl Yermagambet
"""Collect the HTTP control routes."""

from fastapi import APIRouter

from api.controls import configuration_routes, conversation_routes, launch_route, session_gesture_routes

router = APIRouter()
router.include_router(launch_route.router)
router.include_router(session_gesture_routes.router)
router.include_router(configuration_routes.router)
router.include_router(conversation_routes.router)
