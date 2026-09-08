# Copyright (c) 2026 Zhambyl Yermagambet
"""Shared terminal driver and harness composer behavior."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from domain.ids import WindowId
from harness.impl.claude_code.probe import ClaudeCodeComposer
from harness.impl.codex.controls.composer import CodexComposer
from harness.services.composer import with_preserved_draft
from harness.services.terminal_driver import TerminalDriver
from tests.fake_terminal import FakeTerminal

if TYPE_CHECKING:
    from harness.contract import ComposerDriver

DIVIDER_WIDTH = 20
ESCAPE_KEY = "escape"
INSERT_MODE_KEY = "i"
TEST_WINDOW_ID = WindowId("window-one")
TEST_TEXT = "test"


class ClaudeDriver:
    """Represent claude driver."""

    def __init__(
        self,
        text: str,
        mode: str | None,
        unreadable_reads: int = 0,
    ) -> None:
        """Initialize the object."""
        self.text = text
        self.mode = mode
        self._unreadable_reads = unreadable_reads
        self.keys: list[str] = []
        self.insertions: list[str] = []
        self.reads: list[tuple[WindowId, str, bool]] = []
        self.submissions: list[tuple[str, bool]] = []

    def read_text(self, window_id: WindowId, extent: str = "screen", *, ansi: bool = False) -> str:
        """Return text.

        Returns:
            Text.

        """
        self.reads.append((window_id, extent, ansi))
        if self._unreadable_reads:
            self._unreadable_reads -= 1
            return "Claude is updating the terminal"
        divider_line = "─" * DIVIDER_WIDTH
        divider = f"\x1b[m\x1b[38:2:136:136:136m{divider_line}"
        mode = "" if self.mode is None else f"\n-- {self.mode} --"
        return f"{divider}\n\x1b[m\u276f\xa0{self.text}\n{divider}{mode}"

    def send_key(self, _window_id: WindowId, *keys: str) -> bool:
        """Record keys and apply them to the fake composer.

        Returns:
            True for every key request.

        """
        for key in keys:
            self.keys.append(key)
            self._apply_key(key)
        return True

    def insert_text(self, _window_id: WindowId, text: str, *, paste: bool = True) -> bool:
        """Append pasted text to the fake composer.

        Returns:
            True after the text is recorded.

        Raises:
            AssertionError: If paste mode is disabled.

        """
        if not paste:
            message = "the fake requires paste input"
            raise AssertionError(message)
        self.text += text
        self.insertions.append(text)
        return True

    def submit_text(self, _window_id: WindowId, text: str, *, paste: bool = True) -> bool:
        """Record a submission and clear the fake composer.

        Returns:
            True for every submission.

        """
        self.submissions.append((text, paste))
        self.text = ""
        return True

    def as_composer_driver(self) -> ComposerDriver:
        """Expose the operations used by the composer test.

        Returns:
            This test double with the composer protocol type.

        """
        return cast("ComposerDriver", self)

    def _apply_key(self, key: str) -> None:
        if key == ESCAPE_KEY:
            self.mode = "NORMAL"
            return
        if key == INSERT_MODE_KEY and self.mode == "NORMAL":
            self.mode = "INSERT"
            return
        if key in {"ctrl+u", "ctrl+k"}:
            self.text = ""
            return
        if key == "backspace":
            self.text = self.text[:-1]


class CodexDriver:
    """Represent codex driver."""

    def __init__(self, text: str) -> None:
        """Initialize the object."""
        self.text = text
        self.keys: list[str] = []
        self.insertions: list[str] = []
        self.reads: list[tuple[WindowId, str, bool]] = []
        self.submissions: list[tuple[str, bool]] = []

    def read_text(self, window_id: WindowId, extent: str = "screen", *, ansi: bool = False) -> str:
        """Return text.

        Returns:
            Text.

        """
        self.reads.append((window_id, extent, ansi))
        content = self.text or "Ask Codex to do anything"
        return f"\u203a {content}\n\n  gpt-5.6-sol high"

    def send_key(self, _window_id: WindowId, *keys: str) -> bool:
        """Record keys and apply supported text deletion commands.

        Returns:
            True for every key request.

        """
        self.keys.extend(keys)
        if any(key in {"ctrl+u", "ctrl+k"} for key in keys):
            self.text = ""
        elif "backspace" in keys:
            self.text = self.text[:-1]
        return True

    def insert_text(self, _window_id: WindowId, text: str, *, paste: bool = True) -> bool:
        """Append pasted text to the fake composer.

        Returns:
            True after the text is recorded.

        Raises:
            AssertionError: If paste mode is disabled.

        """
        if not paste:
            message = "the fake requires paste input"
            raise AssertionError(message)
        self.text += text
        self.insertions.append(text)
        return True

    def submit_text(self, _window_id: WindowId, text: str, *, paste: bool = True) -> bool:
        """Record a submission and clear the fake composer.

        Returns:
            True if the submitted text is not empty.

        """
        self.submissions.append((text, paste))
        self.text = ""
        return bool(text)

    def as_composer_driver(self) -> ComposerDriver:
        """Expose the operations used by the composer test.

        Returns:
            This test double with the composer protocol type.

        """
        return cast("ComposerDriver", self)


def test_shared_driver_maps_all_text_operations() -> None:
    """Verify the shared driver maps all text operations to one terminal."""
    terminal = FakeTerminal()
    driver = TerminalDriver(terminal.plugin())

    assert driver.insert_text(TEST_WINDOW_ID, "draft")
    assert driver.submit_text(TEST_WINDOW_ID, "message")
    assert driver.send_key(TEST_WINDOW_ID, ESCAPE_KEY, INSERT_MODE_KEY)

    assert (
        terminal.inserted[0][1],
        terminal.submitted[0][1],
        [key for _window, key in terminal.keys],
    ) == ("draft", "message", [ESCAPE_KEY, INSERT_MODE_KEY])


def test_claude_visual_mode_is_normalized() -> None:
    """Verify claude visual mode is normalized before a draft change."""
    driver = ClaudeDriver(TEST_TEXT, "VISUAL")
    composer = ClaudeCodeComposer()

    composer.clear(driver.as_composer_driver(), TEST_WINDOW_ID)
    composer.insert(driver.as_composer_driver(), TEST_WINDOW_ID, TEST_TEXT)

    assert driver.text == TEST_TEXT
    assert driver.keys[:2] == [ESCAPE_KEY, INSERT_MODE_KEY]
    assert driver.insertions == [TEST_TEXT]


def test_claude_standard_editor_does_not_receive() -> None:
    """Verify claude standard editor does not receive vim mode keys."""
    driver = ClaudeDriver(TEST_TEXT, None)

    ClaudeCodeComposer().clear(driver.as_composer_driver(), TEST_WINDOW_ID)

    assert ESCAPE_KEY not in driver.keys
    assert INSERT_MODE_KEY not in driver.keys
    assert not driver.text


def test_claude_clear_waits_for_readable_composer() -> None:
    """Verify a transient redraw does not reject a composer change."""
    driver = ClaudeDriver(TEST_TEXT, None, unreadable_reads=1)

    ClaudeCodeComposer().clear(driver.as_composer_driver(), TEST_WINDOW_ID)

    assert not driver.text
    assert len(driver.reads) > 1


def test_codex_draft_preservation_never_sends_vim() -> None:
    """Verify codex draft preservation never sends vim keys."""
    driver = CodexDriver(TEST_TEXT)
    composer = CodexComposer()
    observed: list[str] = []

    with_preserved_draft(
        composer,
        driver.as_composer_driver(),
        TEST_WINDOW_ID,
        lambda: observed.append(driver.text),
    )

    assert observed == [""]
    assert driver.text == TEST_TEXT
    assert ESCAPE_KEY not in driver.keys
    assert INSERT_MODE_KEY not in driver.keys
