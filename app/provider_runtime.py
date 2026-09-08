# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide installed harness and terminal runtime configuration."""

from typing import Annotated

from fastapi import Depends

from app.injection import singleton
from core import repository as core_repository
from harness import runtime as harness_runtime
from terminal import contract as terminal_contract
from terminal.impl import null
from terminal.impl.pty import plugin as pty_terminal
from terminal.impl.resolution import resolve


@singleton
def harness_runtime_configs() -> harness_runtime.HarnessRuntimeConfigs:
    """Return harness runtime configuration.

    Returns:
        Harness runtime configuration.

    """
    return harness_runtime.default_harness_runtime_configs()


RuntimeConfigs = Annotated[
    harness_runtime.HarnessRuntimeConfigs,
    Depends(harness_runtime_configs),
]


@singleton
def terminal_plugin() -> terminal_contract.TerminalPlugin:
    """Return the installed terminal or the null terminal.

    Returns:
        Installed terminal or the null terminal.

    """
    return resolve() or null.null_plugin()


InstalledTerminal = Annotated[
    terminal_contract.TerminalPlugin,
    Depends(terminal_plugin),
]


@singleton
def model_terminal() -> terminal_contract.TerminalPlugin:
    """Return the private headless model terminal.

    Returns:
        Private headless model terminal.

    """
    return pty_terminal.pty_plugin()


ModelTerminal = Annotated[
    terminal_contract.TerminalPlugin,
    Depends(model_terminal),
]


@singleton
def repositories() -> core_repository.RepositoryQueries:
    """Return Git repository queries.

    Returns:
        Git repository queries.

    """
    return core_repository.RepositoryQueries()


Repositories = Annotated[
    core_repository.RepositoryQueries,
    Depends(repositories),
]
