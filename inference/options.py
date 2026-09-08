# Copyright (c) 2026 Zhambyl Yermagambet
"""Configure executable resolution for default model inference."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from functools import partial

from harness.runtime import (
    HarnessRuntimeConfigs,
    default_harness_runtime_configs,
)
from inference.errors import ExecutableResolverConfigurationError
from inference.executables import runtime_executable

DEFAULT_TIMEOUT_SECONDS = 45.0


@dataclass(frozen=True)
class DefaultModelOptions:
    """Configure runtime resolution and model request timeouts."""

    runtime_configs: HarnessRuntimeConfigs | None = None
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS
    executable_available: Callable[[str], bool] | None = None
    executable_resolver: Callable[[str], str | None] | None = None

    def resolved_runtime_configs(self) -> HarnessRuntimeConfigs:
        """Return explicit or default harness runtime configuration.

        Returns:
            Explicit or default harness runtime configuration.

        """
        return self.runtime_configs or default_harness_runtime_configs()

    def resolved_executable_resolver(
        self,
        runtime_configs: HarnessRuntimeConfigs,
    ) -> Callable[[str], str | None]:
        """Return the one configured executable resolver.

        Returns:
            One configured executable resolver.

        Raises:
            ExecutableResolverConfigurationError: If executable resolver configuration is not valid.

        """
        if self.executable_available is not None and self.executable_resolver is not None:
            raise ExecutableResolverConfigurationError
        if self.executable_resolver is not None:
            return self.executable_resolver
        if self.executable_available is not None:
            return partial(_available_executable, self.executable_available)
        return partial(runtime_executable, runtime_configs)


def _available_executable(
    executable_available: Callable[[str], bool],
    name: str,
) -> str | None:
    if executable_available(name):
        return name
    return None
