# Copyright (c) 2026 Zhambyl Yermagambet
"""Terminal plugin contract tests."""

from __future__ import annotations

import pytest

from terminal.contract import TerminalPlugin
from terminal.impl.kitty.plugin import kitty_plugin
from terminal.impl.null import null_plugin
from terminal.impl.pty.plugin import pty_plugin
from tests.fake_terminal import FakeTerminal, window
from tests.terminal_contract_protocol import SUB_PROTOCOLS, assert_subprotocol, protocol_methods
from tests.terminal_contract_remote import FakeRemote


@pytest.mark.parametrize(
    "plugin",
    [null_plugin(), kitty_plugin(FakeRemote()), pty_plugin()],
    ids=["none", "kitty", "pty"],
)
def test_terminal_subprotocols(plugin: TerminalPlugin) -> None:
    """Verify every terminal implements only its five subprotocols."""
    assert isinstance(plugin, TerminalPlugin)
    for field, protocol in SUB_PROTOCOLS.items():
        assert_subprotocol(plugin, field, protocol)


def test_fake_terminal_contract() -> None:
    """Verify the shared fake terminal matches the contract."""
    plugin = FakeTerminal(windows=[window("window-one")]).plugin()
    for field, protocol in SUB_PROTOCOLS.items():
        implementation = getattr(plugin, field)
        for name in protocol_methods(protocol):
            assert callable(getattr(implementation, name))
