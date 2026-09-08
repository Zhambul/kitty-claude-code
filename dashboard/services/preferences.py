# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide application preference services."""

import time
from collections.abc import Callable

from app import application_preference_resources as resources
from dashboard.services.preference_reads import ApplicationPreferenceReadOperations
from dashboard.services.preference_writes import ApplicationPreferenceWriteOperations


class ApplicationPreferenceService(ApplicationPreferenceReadOperations, ApplicationPreferenceWriteOperations):
    """Provide application preference read and write operations."""

    def __init__(
        self,
        core: resources.ApplicationPreferenceCore,
        settings: resources.ApplicationPreferenceSettings,
        signals: resources.ApplicationPreferenceSignals,
        clock: Callable[[], float] = time.time,
    ) -> None:
        """Initialize the object."""
        self.core = core
        self.settings = settings
        self.signals = signals
        self.clock = clock
