# Copyright (c) 2026 Zhambyl Yermagambet
"""Claude Code question screens remain identifiable when the viewport clips them."""

import pytest

from domain.ids import WindowId
from harness.impl.claude_code.canonical.records import Question, QuestionOption
from harness.impl.claude_code.controls import ask_flow, ask_navigation, askdialog
from harness.impl.claude_code.controls.ask_models import AskError, AskOutcome, AskRequest, NavigationContext
from harness.impl.claude_code.controls.askdialog_screen import current_question
from harness.impl.claude_code.controls.screen_driver import (
    SCREEN_LIMIT,
    StepError,
    failure_detail,
)
from tests.question_dialog_drivers import ClippedCursorDriver, FrozenCursorDriver, ResizeDriver


def test_screen_driver_failure_keeps_only_bounded() -> None:
    """Verify screen driver failure keeps only a bounded screen tail."""
    screen_tail = "x" * SCREEN_LIMIT
    screen = f"discarded-prefix:{screen_tail}"

    detail = failure_detail(StepError("open", "menu missing", screen))

    assert detail.startswith("open: menu missing; screen=")
    assert "discarded-prefix" not in detail
    assert "x" * SCREEN_LIMIT in detail


def test_cursor_navigation_reveals_selected_row() -> None:
    """Verify cursor navigation reveals a selected row above the viewport."""
    driver = ClippedCursorDriver()

    screen = ask_navigation.cursor_to(
        NavigationContext(driver, WindowId("window"), lambda _seconds: None),
        lambda row: row.digit == "1",
        "option 1",
    )

    assert "\u276f 1. Blue" in screen


def test_cursor_navigation_does_not_repeat() -> None:
    """Verify cursor navigation does not repeat an unverified down key."""
    driver = FrozenCursorDriver()

    with pytest.raises(AskError, match="down key had no visible effect"):
        ask_navigation.cursor_to(
            NavigationContext(driver, WindowId("window"), lambda _seconds: None),
            lambda row: row.digit == "2",
            "option 2",
        )

    assert driver.keys == ["down"]


def test_question_driver_restores_temporary(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify question driver restores temporary viewport growth."""
    driver = ResizeDriver()
    monkeypatch.setattr(
        ask_flow,
        "drive_dialog",
        lambda *_args, **_kwargs: AskOutcome.SUBMITTED,
    )

    outcome = askdialog.drive(
        driver,
        WindowId("window"),
        AskRequest([], []),
        sleep=lambda _seconds: None,
    )

    assert outcome == AskOutcome.SUBMITTED
    assert driver.resizes == [36, -36]


def test_visible_unique_options_identify_question() -> None:
    """Verify visible unique options identify a question whose prompt is above the viewport."""
    questions = [
        Question(
            question="Which base should I use?",
            options=[QuestionOption(label="Remote base"), QuestionOption(label="Local base")],
        ),
        Question(
            question="Which regression scope should I use?",
            options=[
                QuestionOption(label="Full regression"),
                QuestionOption(label="Feature only"),
                QuestionOption(label="Blocker only"),
            ],
        ),
    ]
    clipped_screen = """
      1. Full regression
         Cover every affected adapter.
    \u276f 2. Feature only
         Keep the checks on this feature.
      3. Blocker only
         Report the blocker without more checks.
      4. Type something.

      Enter to select
    """

    assert current_question(clipped_screen, questions) == 1


def test_repeated_option_labels_do_not_guess() -> None:
    """Verify repeated option labels do not guess a clipped question."""
    questions = [
        Question(question="First?", options=[QuestionOption(label="Yes")]),
        Question(question="Second?", options=[QuestionOption(label="Yes")]),
    ]
    clipped_screen = """
    \u276f 1. Yes
      2. Type something.
      Enter to select
    """

    assert current_question(clipped_screen, questions) is None
