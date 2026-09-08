# Copyright (c) 2026 Zhambyl Yermagambet
"""Select the terminal plugin for this process."""

import importlib
import os
from pathlib import Path

from terminal.contract import TerminalPlugin

PLUGIN_FACTORY_NAME = "build_plugin"
DETECTOR_NAME = "detect_plugin"
NO_TERMINAL_NAME = "none"
NO_TERMINAL_MODULE = "terminal.impl.null"


def _load_plugin(module_name: str) -> TerminalPlugin:
    plugin_module = importlib.import_module(module_name)
    plugin_factory = getattr(plugin_module, PLUGIN_FACTORY_NAME, None)
    if not callable(plugin_factory):
        message = f"{module_name} must export {PLUGIN_FACTORY_NAME}"
        raise TypeError(message)
    plugin = plugin_factory()
    if not isinstance(plugin, TerminalPlugin):
        message = f"{module_name}.{PLUGIN_FACTORY_NAME} must return a TerminalPlugin"
        raise TypeError(message)
    return plugin


def _plugin_module_name(name: str) -> str:
    if name == NO_TERMINAL_NAME:
        return NO_TERMINAL_MODULE
    descriptor = Path(__file__).resolve().parent / name / "plugin.py"
    if not descriptor.is_file():
        message = f"unsupported terminal: {name}"
        raise ValueError(message)
    return f"terminal.impl.{name}.plugin"


def _detected_plugin() -> TerminalPlugin | None:
    for descriptor in sorted(Path(__file__).resolve().parent.glob("*/plugin.py")):
        plugin = _plugin_from_descriptor(descriptor)
        if plugin is not None:
            return plugin
    return None


def _plugin_from_descriptor(descriptor: Path) -> TerminalPlugin | None:
    implementation_name = descriptor.parent.name
    module_name = f"terminal.impl.{implementation_name}.plugin"
    detector = getattr(importlib.import_module(module_name), DETECTOR_NAME, None)
    if not callable(detector):
        return None
    plugin = detector()
    if plugin is not None and not isinstance(plugin, TerminalPlugin):
        message = f"{module_name}.{DETECTOR_NAME} must return a TerminalPlugin or None"
        raise TypeError(message)
    return plugin


def resolve() -> TerminalPlugin | None:
    """Return the selected terminal plugin.

    Returns:
        The selected terminal plugin, if one is available.

    """
    pinned = (os.environ.get("BAQYLAU_TERMINAL") or "").strip().lower()
    if pinned:
        return _load_plugin(_plugin_module_name(pinned))
    return _detected_plugin()
