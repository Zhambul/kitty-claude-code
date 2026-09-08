# Copyright (c) 2026 Zhambyl Yermagambet
"""Cross-harness canonical translation tests from native fixture shapes."""

from __future__ import annotations

import pytest

from domain import (
    ids as domain_ids,
)
from harness.impl.claude_code.controls import (
    rewind_flow,
    rewind_models,
    rewind_navigation,
    rewind_screen,
    rewindmenu,
)
from tests.plugin_tests import vocabulary as fixture
from tests.plugin_tests.control_basic_support import (
    raise_confirm_menu_error,
)
from tests.plugin_tests.control_driver_support import (
    RewindScreenDriver,
)
from tests.plugin_tests.control_state_values import (
    PRIMARY_WINDOW,
)


@pytest.mark.parametrize(
    (fixture.SCREEN, "keys"),
    [
        (
            "  Rewind\nConfirm you want to restore\n\u276f 1. Restore conversation\n  2. Cancel",
            [fixture.ENTER],
        ),
        (
            "  Rewind\nConfirm you want to restore\n  1. Restore conversation\n\u276f 2. Cancel",
            [fixture.UP, fixture.ENTER],
        ),
    ],
)
def test_claude_rewind_confirmation_uses_cursor(
    screen: str,
    keys: list[str],
) -> None:
    """Verify claude rewind confirmation uses cursor navigation."""
    driver = RewindScreenDriver(
        screen,
        {
            (fixture.UP,): "  Rewind\nConfirm you want to restore\n\u276f 1. Restore conversation\n  2. Cancel",
            (fixture.ENTER,): "",
        },
    )

    rewind_navigation.select_confirm(
        rewind_models.RewindContext(driver, PRIMARY_WINDOW, lambda _seconds: None),
        fixture.ONE_TEXT,
    )

    assert driver.keys == keys


def test_claude_rewind_list_is_open_when_terminal() -> None:
    """Verify claude rewind list is open when the terminal clips its footer."""
    screen = """Previous output

  Rewind

  Restore the code and/or conversation to the point before…

   ↑ 1 more above

    Use the Edit tool to replace the old value with…
    marker.txt +1 -1

  \u276f (current)"""

    assert rewind_screen.menu_open(screen)


def test_claude_rewind_list_accepts_new_three() -> None:
    """Verify claude rewind list accepts the new three space header indent."""
    screen = """Previous output

   Rewind

   Restore the code and/or conversation to the point before…

    ↑ 1 more above

     Reply only with the word second.
     No code changes

   \u276f (current)

   Enter to continue · Esc to cancel"""

    assert rewind_screen.menu_open(screen)


def test_claude_rewind_confirmation_waits() -> None:
    """Verify claude rewind confirmation waits for the requested option."""
    partial = """  Rewind

  Confirm you want to restore to the point before you sent this message:

  The conversation will be forked."""
    confirmation_options = """

  \u276f 1. Restore code and conversation
    2. Restore conversation
    3. Restore code"""
    complete = partial + confirmation_options

    assert not rewind_screen.confirm_ready(partial, "restore code", fixture.CODE)
    assert rewind_screen.confirm_ready(complete, "restore code", fixture.CODE)


def test_claude_rewind_confirmation_reveals() -> None:
    """Verify claude rewind confirmation reveals options below the viewport."""
    hidden_screen = """  Rewind

  Confirm you want to restore to the point before you sent this message:

  The conversation will be forked."""
    revealed_screen = (
        f"{hidden_screen}\n\n  \u276f 1. Restore code and conversation\n"
        "    2. Restore conversation\n    3. Restore code"
    )
    driver = RewindScreenDriver(
        hidden_screen,
        {(fixture.DOWN,): revealed_screen},
    )

    screen, found = rewind_navigation.scan_confirm(
        rewind_models.RewindContext(driver, PRIMARY_WINDOW, lambda _seconds: None),
        "restore code",
        fixture.CODE,
        fixture.DOWN,
    )

    assert found
    assert "Restore code" in screen
    assert driver.keys == [fixture.DOWN]


def test_claude_rewind_restores_temporary(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify claude rewind restores a temporary viewport growth."""
    driver = RewindScreenDriver("", {}, line_count=24)
    monkeypatch.setattr(
        rewind_flow,
        "drive_menu",
        raise_confirm_menu_error,
    )

    with pytest.raises(rewind_models.MenuError):
        rewindmenu.drive(
            driver,
            domain_ids.WindowId(fixture.WINDOW_ONE_ID),
            rewind_models.RewindRequest("target prompt", fixture.CODE),
            sleep=lambda _seconds: None,
        )

    assert driver.resizes == [16, -16]
