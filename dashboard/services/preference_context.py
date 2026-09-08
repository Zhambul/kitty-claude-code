# Copyright (c) 2026 Zhambyl Yermagambet
"""Define dependencies for application preference operations."""

from collections.abc import Callable
from typing import Protocol

from app import application_preference_resources as resources


class ApplicationPreferenceContext(Protocol):
    """Provide dependencies for application preference operations."""

    core: resources.ApplicationPreferenceCore
    settings: resources.ApplicationPreferenceSettings
    signals: resources.ApplicationPreferenceSignals
    clock: Callable[[], float]
