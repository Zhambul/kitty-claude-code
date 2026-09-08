# Copyright (c) 2026 Zhambyl Yermagambet
"""Terminal protocol inspection helpers."""

from __future__ import annotations

import inspect
from types import MappingProxyType

from terminal.contract import (
    TerminalInput,
    TerminalMetadata,
    TerminalPanes,
    TerminalPlugin,
    TerminalTabs,
    TerminalViewport,
)

type TerminalProtocol = TerminalTabs | TerminalPanes | TerminalMetadata | TerminalInput | TerminalViewport

SUB_PROTOCOLS: MappingProxyType[str, type[TerminalProtocol]] = MappingProxyType({
    "tabs": TerminalTabs,
    "panes": TerminalPanes,
    "metadata": TerminalMetadata,
    "input": TerminalInput,
    "viewport": TerminalViewport,
})


def protocol_methods(protocol: type[TerminalProtocol]) -> set[str]:
    """Return public protocol methods.

    Returns:
        Public protocol methods.

    """
    names = set()
    for name, member in inspect.getmembers(protocol, inspect.isfunction):
        if not name.startswith("_") and callable(member):
            names.add(name)
    return names


def assert_subprotocol(
    plugin: TerminalPlugin,
    field: str,
    protocol: type[TerminalProtocol],
) -> None:
    """Verify that one implementation matches one protocol."""
    implementation = getattr(plugin, field)
    declared = protocol_methods(protocol)
    public = _public_callables(implementation)
    missing = declared - public
    extra = public - declared
    assert not missing, f"{plugin.name}.{field} is missing {missing}"
    assert not extra, f"{plugin.name}.{field} adds {extra}"


def _public_callables(implementation: object) -> set[str]:
    return {
        name for name, _member in inspect.getmembers(implementation, callable)
        if not name.startswith("_")
    }
