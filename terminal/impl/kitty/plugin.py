# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the kitty terminal plugin."""

from terminal.contract import TerminalPlugin
from terminal.impl.kitty import remote as kitty_remote_api
from terminal.impl.kitty.input import KittyInput
from terminal.impl.kitty.metadata import KittyMetadata
from terminal.impl.kitty.panes import KittyPanes
from terminal.impl.kitty.tabs import KittyTabs
from terminal.impl.kitty.viewport import KittyViewport


def kitty_plugin(kitty_remote: kitty_remote_api.KittyRemote | None = None) -> TerminalPlugin:
    """Return the kitty terminal plugin.

    Returns:
        The kitty terminal plugin.

    """
    remote = kitty_remote_api.KittyRemote() if kitty_remote is None else kitty_remote
    metadata = KittyMetadata(remote)
    return TerminalPlugin(
        name="kitty",
        tabs=KittyTabs(remote),
        panes=KittyPanes(remote, metadata),
        metadata=metadata,
        input=KittyInput(remote),
        viewport=KittyViewport(remote),
    )


def build_plugin() -> TerminalPlugin:
    """Build the kitty terminal plugin.

    Returns:
        The kitty terminal plugin.

    """
    return kitty_plugin()


def detect_plugin() -> TerminalPlugin | None:
    """Return the plugin when kitty is available.

    Returns:
        The plugin when kitty is available.

    """
    return build_plugin() if kitty_remote_api.find_kitten() else None
