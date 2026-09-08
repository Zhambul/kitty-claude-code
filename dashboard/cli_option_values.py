# Copyright (c) 2026 Zhambyl Yermagambet
"""Own dashboard option values."""

from types import MappingProxyType

LAUNCH_VARIABLES = MappingProxyType({
    "--port": "BAQYLAU_DASHBOARD_PORT",
    "--data-dir": "BAQYLAU_DATA_DIR",
})


LOG_FLAG = "--log"


HARNESS_FLAGS = (
    "--harness-executable",
    "--harness-config-dir",
    "--harness-settings-file",
)
