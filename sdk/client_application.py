# Copyright (c) 2026 Zhambyl Yermagambet
"""Split SDK client implementation."""

from __future__ import annotations

from sdk import application_models, transport
from sdk.client_adapters import (
    APPLICATION,
    HEALTH,
)
from sdk.client_wait import (
    _health_wait_description,
    wait_for,
)


class ApplicationResource:
    """Represent application resource."""

    def __init__(self, transport: transport.HttpTransport) -> None:
        """Initialize the application resource."""
        self.transport = transport

    def health(self) -> application_models.health_response.HealthResponse:
        """Return the health.

        Returns:
            Health.

        """
        return self.transport.get("/api/health", HEALTH)

    def wait_until_ready(self, timeout: float = 30.0) -> application_models.health_response.HealthResponse:
        """Wait until ready.

        Returns:
            The health response.

        """
        last_error: list[str] = []
        return wait_for(
            lambda: _health_wait_description(last_error),
            lambda: self._read_health(last_error),
            timeout=timeout,
            interval=0.1,
        )

    def state(self) -> application_models.global_application_response.GlobalApplicationResponse:
        """Return the state.

        Returns:
            State.

        """
        return self.transport.get("/api/application", APPLICATION)

    def _read_health(
        self,
        last_error: list[str],
    ) -> application_models.health_response.HealthResponse | None:
        try:
            return self.health()
        except (transport.ApiFailureError, OSError) as error:
            last_error.clear()
            last_error.append(str(error))
            return None
