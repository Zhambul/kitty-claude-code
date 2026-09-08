# Copyright (c) 2026 Zhambyl Yermagambet
"""Own dashboard server."""

import os
from pathlib import Path
from typing import TYPE_CHECKING

from dashboard.cli_health_values import PRIVATE_FILE_MODE
from dashboard.cli_output import _error

if TYPE_CHECKING:
    from harness.runtime import HarnessRuntimeConfigs


def _redirect(log_path: str) -> None:
    """Send this process's own output to a file, descriptors and all.

    `dup2` rather than reassigning `sys.stdout`, because the interesting output
    is not ours: uvicorn writes to the descriptor, and so does anything it
    imports. A caller redirecting with a shell got both; so must this.
    """
    Path(log_path).parent.mkdir(exist_ok=True, parents=True)
    open_flags = os.O_WRONLY | os.O_CREAT | os.O_APPEND
    with os.fdopen(
        os.open(log_path, open_flags, PRIVATE_FILE_MODE),
        "ab",
    ) as log_file:
        file_descriptor = log_file.fileno()
        os.dup2(file_descriptor, 1)
        os.dup2(file_descriptor, 2)


def _serve(harness_runtime_configs: "HarnessRuntimeConfigs") -> int:
    from dashboard.frontend_build import (  # noqa: PLC0415 — startup validation stays lazy
        FrontendBuildError,
        validate_frontend_build,
    )

    try:
        validate_frontend_build()
    except FrontendBuildError as error:
        _error(f"dashboard cannot start: {error}")
        return 1
    from api.runtime import ApplicationConfig, DashboardApplication  # noqa: PLC0415 — configuration precedes imports

    return (
        DashboardApplication(
            ApplicationConfig.from_environment(harness_runtime_configs),
        )
        .run()
        .exit_code
    )
