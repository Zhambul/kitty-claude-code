# Copyright (c) 2026 Zhambyl Yermagambet
"""Harness dependencies for terminal hook tests."""

from harness.hooks.gateway import (
    HookGatewayService as HookGatewayService,
    UnknownHookHarnessError as UnknownHookHarnessError,
)
from harness.impl.discovery import installed as installed
from harness.registry import HarnessRegistry as HarnessRegistry
