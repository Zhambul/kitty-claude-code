# Copyright (c) 2026 Zhambyl Yermagambet
"""Hook composer tests."""

from __future__ import annotations

from typing import TYPE_CHECKING

from domain.ids import (
    WindowId,
)
from harness.impl.claude_code.controls import (
    composer_clear,
    tui as claude_tui,
)
from harness.services.terminal_driver import TerminalDriver
from tests.fake_terminal import FakeTerminal
from tests.plugin_tests import support_terminal, vocabulary as fixture
from tests.plugin_tests.hook_composer_support import (
    ClearComposerDriver,
    clipboard_has_no_image,
    submission_marker_is_visible,
)

if TYPE_CHECKING:
    import pytest

EXPECTED_ENTER_ATTEMPTS = 2


def test_type_command_verifies_submit_and_retries(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify type command verifies the submit and retries the enter."""
    monkeypatch.setattr("harness.impl.claude_code.controls.tui.time.sleep", lambda _seconds: None)
    monkeypatch.setattr("harness.impl.claude_code.controls.clipboard_image.clear_image", clipboard_has_no_image)
    monkeypatch.setattr(
        claude_tui,
        "_submission_pending",
        submission_marker_is_visible,
    )

    retried = support_terminal.SubmitProbeDriver(sticky=1)
    ok, _ = claude_tui.type_command(retried, WindowId(fixture.WINDOW_FIRST_ID), "hello from the dashboard")
    assert ok is True
    assert retried.enters == 1

    stuck = support_terminal.SubmitProbeDriver(sticky=fixture.EXHAUSTED_RETRY_COUNT)
    ok, _ = claude_tui.type_command(stuck, WindowId(fixture.WINDOW_FIRST_ID), "hello from the dashboard")
    assert ok is False
    assert stuck.enters == EXPECTED_ENTER_ATTEMPTS


def test_type_command_confirms_attachment_prompt(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify type command confirms an attachment prompt with the enter retry budget."""
    monkeypatch.setattr("harness.impl.claude_code.controls.tui.time.sleep", lambda _seconds: None)
    monkeypatch.setattr("harness.impl.claude_code.controls.clipboard_image.clear_image", clipboard_has_no_image)
    monkeypatch.setattr(
        claude_tui,
        "_submission_pending",
        submission_marker_is_visible,
    )
    driver = support_terminal.SubmitProbeDriver(sticky=1)

    ok, _ = claude_tui.type_command(
        driver,
        WindowId(fixture.WINDOW_FIRST_ID),
        "inspect it",
        ensure_submit=True,
    )

    assert ok is True
    assert driver.enters == EXPECTED_ENTER_ATTEMPTS


def test_type_command_rejects_screen(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify type command rejects a screen without a composer."""
    monkeypatch.setattr(
        claude_tui,
        "poll_until",
        lambda _driver, _window, _predicate, _timeout: ("working", False),
    )
    driver = support_terminal.SubmitProbeDriver(sticky=1)

    ok, cleared = claude_tui.type_command(driver, WindowId(fixture.WINDOW_FIRST_ID), fixture.HELLO)

    assert ok is False
    assert cleared is False
    assert not driver.box


def test_claude_clear_input_removes_each_restored() -> None:
    """Verify claude clear input removes each restored logical line."""
    driver = ClearComposerDriver(["first line", "second line", "third line"])
    line_count = len(driver.lines)

    killed = composer_clear.clear_input(
        driver,
        WindowId(fixture.WINDOW_ONE_ID),
        "first line second line third line",
        sleep=lambda _seconds: None,
    )

    assert killed == line_count
    assert not driver.lines
    assert driver.keys == [
        fixture.CLEAR_BEFORE_CURSOR_KEY,
        fixture.CLEAR_AFTER_CURSOR_KEY,
        fixture.BACKSPACE,
        fixture.CLEAR_BEFORE_CURSOR_KEY,
        fixture.CLEAR_AFTER_CURSOR_KEY,
        fixture.BACKSPACE,
        fixture.CLEAR_BEFORE_CURSOR_KEY,
        fixture.CLEAR_AFTER_CURSOR_KEY,
    ]


def test_claude_clear_input_waits_for_delayed() -> None:
    """Verify claude clear input waits for delayed screen updates."""
    driver = ClearComposerDriver(
        ["restored first line", "restored second line"],
        clear_is_delayed=True,
    )
    line_count = len(driver.lines)

    killed = composer_clear.clear_input(
        driver,
        WindowId(fixture.WINDOW_ONE_ID),
        "restored first line\nrestored second line",
        sleep=lambda _seconds: None,
    )

    assert killed == line_count
    assert not driver.lines


def test_claude_clear_input_does_not_accept() -> None:
    """Verify claude clear input does not accept a prompt suggestion."""
    divider = fixture.GREY_ANSI_SEQUENCE + fixture.DIVIDER_CHARACTER * fixture.DIVIDER_WIDTH
    screen = f"{divider}\n\x1b[m\u276f\xa0\x1b[22;2mshow me the audit records\n{divider}"
    terminal = FakeTerminal(screen_text=screen)

    killed = composer_clear.clear_input(
        TerminalDriver(terminal.plugin()),
        WindowId(fixture.WINDOW_ONE_ID),
    )

    assert killed == 0
    assert not terminal.keys
