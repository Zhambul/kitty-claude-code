# Copyright (c) 2026 Zhambyl Yermagambet
"""Concrete harness plugin registration — a validated name-to-plugin map."""

from __future__ import annotations

from typing import TYPE_CHECKING

from domain.errors import UnknownReferenceError
from domain.events import SCHEMA_VERSION
from harness.contract import HarnessReactorProvider
from harness.models.controls import (
    ControlName,
)

if TYPE_CHECKING:
    from domain.ids import HarnessName
    from harness.contract import HarnessPlugin


class HarnessRegistryError(UnknownReferenceError):
    """Represent harness registry error.

    Raised for a bad REGISTRATION (a duplicate name, a version mismatch) and
        for a bad LOOKUP — and the lookup is the one a request can cause, by naming
        a harness in a URL. As a RuntimeError that reached no handler, an unknown
        harness in `/api/harnesses/{harness}/catalog` was answered as a 500; it is
        the caller's mistake and now says so. A registration failure happens at boot,
        where nothing is serving and the type is irrelevant.
    """


def _validate_automatic_naming(harness_plugin: HarnessPlugin) -> None:
    has_native_handler = bool(
        harness_plugin.controller and ControlName.AUTO_NAME_SESSION in harness_plugin.controller.handlers,
    )
    supports_native_naming = harness_plugin.harness_info.supports_native_automatic_renaming
    plugin_name = harness_plugin.harness_info.name
    if supports_native_naming and not has_native_handler:
        message = f"harness {plugin_name!r} advertises native automatic naming without an auto-name handler"
        raise HarnessRegistryError(message)
    if not supports_native_naming and has_native_handler:
        message = f"harness {plugin_name!r} registers native automatic naming without declaring native support"
        raise HarnessRegistryError(message)


class HarnessRegistry(HarnessReactorProvider):
    """Represent harness registry."""

    def __init__(self) -> None:
        """Initialize the object."""
        self._plugins: dict[HarnessName, HarnessPlugin] = {}

    def register(self, harness_plugin: HarnessPlugin) -> None:
        """Register.

        Raises:
            HarnessRegistryError: If the harness registry is not valid.

        """
        name = harness_plugin.harness_info.name
        if name in self._plugins:
            message = f"duplicate harness: {name}"
            raise HarnessRegistryError(message)
        canonical_version = harness_plugin.harness_info.canonical_version
        if canonical_version != SCHEMA_VERSION:
            message = f"harness {name!r} uses canonical version {canonical_version}, expected {SCHEMA_VERSION}"
            raise HarnessRegistryError(
                message,
            )
        if harness_plugin.harness_info.default_for_launch and any(
            registered.harness_info.default_for_launch for registered in self._plugins.values()
        ):
            message = "multiple harnesses are marked as the launch default"
            raise HarnessRegistryError(message)
        self._plugins[name] = harness_plugin

    def validate(self) -> None:
        """Validate validate.

        Raises:
            HarnessRegistryError: If the harness registry is not valid.

        """
        launchable = [plugin for plugin in self._plugins.values() if plugin.launcher is not None]
        defaults = [plugin for plugin in launchable if plugin.harness_info.default_for_launch]
        if launchable and not defaults:
            message = "no launchable harness is marked as the launch default"
            raise HarnessRegistryError(message)
        for plugin in self._plugins.values():
            _validate_automatic_naming(plugin)

    def plugin(self, harness: HarnessName) -> HarnessPlugin:
        """Return the plugin.

        Returns:
            Plugin.

        Raises:
            HarnessRegistryError: If the harness registry is not valid.

        """
        try:
            return self._plugins[harness]
        except KeyError as error:
            message = f"unregistered harness: {harness}"
            raise HarnessRegistryError(message) from error

    def plugins(self) -> tuple[HarnessPlugin, ...]:
        """Return the plugins.

        Returns:
            Plugins.

        """
        return tuple(self._plugins[name] for name in sorted(self._plugins))
