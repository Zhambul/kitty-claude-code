# Copyright (c) 2026 Zhambyl Yermagambet
"""Steps that save and check terminal focus."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pytest_bdd import parsers, then, when

if TYPE_CHECKING:
    from tests.e2e.testkit.references import References
    from tests.e2e.testkit.terminal_models import TerminalFocus
    from tests.e2e.testkit.terminals import RealTerminalDriver


@when(parsers.parse('I remember current terminal focus as "{focus_name}"'))
def remember_current_terminal_focus(
    real_terminal_driver: RealTerminalDriver,
    terminal_focuses: References[TerminalFocus],
    focus_name: str,
) -> None:
    """Save the current terminal focus."""
    terminal_focuses.bind(focus_name, real_terminal_driver.current_focus())


@then(parsers.parse('current terminal focus remains "{focus_name}"'))
def current_terminal_focus_remains(
    real_terminal_driver: RealTerminalDriver,
    terminal_focuses: References[TerminalFocus],
    focus_name: str,
) -> None:
    """Verify the saved terminal focus remains current."""
    real_terminal_driver.assert_focus_preserved(terminal_focuses.get(focus_name))
