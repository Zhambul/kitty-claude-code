# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide read routes for application preferences."""

from fastapi import APIRouter

from api.application.mapper import preferences as mapper
from api.application.models.preferences.global_application_response import GlobalApplicationResponse
from api.application.models.preferences.push_configuration_response import PushConfigurationResponse
from app.provider_application_preferences import ApplicationPreferences
from app.provider_preference_storage import PushSigningKeys
from notify.channels import webpush

router = APIRouter()


@router.get("/api/application/push-configuration")
def push_configuration(signing_keys: PushSigningKeys) -> PushConfigurationResponse:
    """Return the Web Push configuration.

    Returns:
        The push configuration.

    """
    key = webpush.public_key(signing_keys)
    return PushConfigurationResponse(enabled=bool(webpush.enabled() and key), key=key)


@router.get("/api/application")
def application_state(application_preferences: ApplicationPreferences) -> GlobalApplicationResponse:
    """Return the browser-owned application state.

    Returns:
        The application state.

    """
    return mapper.global_application(application_preferences.snapshot())
