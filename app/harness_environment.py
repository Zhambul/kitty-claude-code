# Copyright (c) 2026 Zhambyl Yermagambet
"""Build environment variables for terminal-launched harnesses."""

import os

from terminal.models.tabs import EnvironmentVariable

DEFAULT_DASHBOARD_PORT = "8377"


def launch_environment() -> tuple[EnvironmentVariable, ...]:
    """Return environment variables for each launched harness.

    Returns:
        Environment variables for each launched harness.

    """
    return (
        EnvironmentVariable(
            "BAQYLAU_DASHBOARD_PORT",
            os.environ.get("BAQYLAU_DASHBOARD_PORT", DEFAULT_DASHBOARD_PORT),
        ),
        EnvironmentVariable("PATH", os.environ.get("PATH", os.defpath)),
    )
