# Copyright (c) 2026 Zhambyl Yermagambet
"""Typed startup configuration for installed harnesses."""

from __future__ import annotations

import os
from dataclasses import dataclass
from itertools import starmap
from pathlib import Path
from typing import TYPE_CHECKING

from domain.ids import HarnessName

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping

CODEX_EXECUTABLE = "codex"


@dataclass(frozen=True)
class HarnessRuntimeConfig:
    """Represent harness runtime config."""

    executable: str
    configuration_directory: Path
    settings_file: Path | None = None
    use_vendor_default_configuration: bool = False


@dataclass(frozen=True)
class HarnessRuntimeEntry:
    """Represent harness runtime entry."""

    harness: HarnessName
    config: HarnessRuntimeConfig


class HarnessRuntimeConfigs:
    """One runtime configuration, indexed by harness name."""

    def __init__(
        self,
        entries: Iterable[HarnessRuntimeEntry],
    ) -> None:
        """Initialize the object.

        Raises:
            ValueError: If an input value is not valid.

        """
        entry_values = tuple(entries)
        by_harness = {entry.harness: entry.config for entry in entry_values}
        if len(by_harness) != len(entry_values):
            message = "duplicate harness runtime configuration"
            raise ValueError(message)
        self._by_harness: Mapping[HarnessName, HarnessRuntimeConfig] = by_harness

    def for_harness(self, harness: HarnessName) -> HarnessRuntimeConfig:
        """Return the for harness.

        Returns:
            For harness.

        Raises:
            ValueError: If an input value is not valid.

        """
        try:
            return self._by_harness[harness]
        except KeyError as error:
            message = f"missing runtime configuration for {harness}"
            raise ValueError(message) from error

    def entries(self) -> tuple[HarnessRuntimeEntry, ...]:
        """Return the entries.

        Returns:
            Entries.

        """
        return tuple(starmap(HarnessRuntimeEntry, self._by_harness.items()))

    def updated(
        self,
        harness: HarnessName,
        harness_runtime_config: HarnessRuntimeConfig,
    ) -> HarnessRuntimeConfigs:
        """Return the updated.

        Returns:
            Updated.

        """
        return HarnessRuntimeConfigs(
            (
                HarnessRuntimeEntry(
                    name,
                    harness_runtime_config if name == harness else current,
                )
                for name, current in self._by_harness.items()
            ),
        )


def _installed_executable(candidates: tuple[str, ...], fallback: str) -> str:
    for candidate in candidates:
        if Path(candidate).is_file() and os.access(candidate, os.X_OK):
            return candidate
    return fallback


def default_harness_runtime_configs() -> HarnessRuntimeConfigs:
    """Return the default harness runtime configs.

    Returns:
        Default harness runtime configs.

    """
    home = Path.home()
    native_codex_candidates = tuple(
        str(candidate)
        for candidate in sorted(
            (
                home
                / ".hermes"
                / "node"
                / "lib"
                / "node_modules"
                / "@openai"
                / CODEX_EXECUTABLE
                / "node_modules"
                / "@openai"
            ).glob("codex-*/vendor/*/bin/codex"),
        )
    )
    return HarnessRuntimeConfigs(
        (
            HarnessRuntimeEntry(
                HarnessName.CLAUDE_CODE,
                HarnessRuntimeConfig(
                    _installed_executable(
                        (
                            str(home / ".local" / "bin" / "claude"),
                            "/opt/homebrew/bin/claude",
                            "/usr/local/bin/claude",
                        ),
                        "claude",
                    ),
                    home / ".claude",
                    use_vendor_default_configuration=True,
                ),
            ),
            HarnessRuntimeEntry(
                HarnessName.CODEX,
                HarnessRuntimeConfig(
                    _installed_executable(
                        (
                            *native_codex_candidates,
                            str(home / ".hermes" / "node" / "bin" / CODEX_EXECUTABLE),
                            "/opt/homebrew/bin/codex",
                            "/usr/local/bin/codex",
                            str(home / ".local" / "bin" / CODEX_EXECUTABLE),
                        ),
                        CODEX_EXECUTABLE,
                    ),
                    home / ".codex",
                ),
            ),
        ),
    )
