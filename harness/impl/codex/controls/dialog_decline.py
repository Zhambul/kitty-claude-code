# Copyright (c) 2026 Zhambyl Yermagambet
"""Decline Codex question-dialog prompts."""

import time
from collections.abc import Callable
from functools import partial

from domain.ids import WindowId
from harness.contract import ComposerDriver
from harness.impl.codex.controls.dialog_models import CodexAskError, DialogOutcome, Prompt
from harness.impl.codex.controls.dialog_navigation import STEP_TIMEOUT_SECONDS, add_note, cursor_to
from harness.impl.codex.controls.dialog_screen_rows import NONE_LABEL, none_row
from harness.impl.codex.controls.dialog_screen_state import current_question, dialog_open, poll, screen_text


def decline(
    composer_driver: ComposerDriver,
    window_id: WindowId,
    questions: list[Prompt],
    discussion: str = "",
    sleep: Callable[[float], None] = time.sleep,
) -> DialogOutcome:
    """Submit the least-committal answer to the last question.

    Returns:
        The submitted dialog outcome after the dialog closes.

    Raises:
        CodexAskError: If the last question has no row for declining all choices.

    """
    question_count = _move_to_last_question(composer_driver, window_id, sleep)
    question_index = question_count - 1
    prompt = questions[question_index] if 0 <= question_index < len(questions) else Prompt()
    row = none_row(screen_text(composer_driver, window_id), prompt)
    if not row:
        msg = "noneof"
        raise CodexAskError(msg, f"no {NONE_LABEL!r} row to decline with")
    cursor_to(composer_driver, window_id, row, sleep)
    add_note(composer_driver, window_id, (discussion or "Continue in chat.").strip(), sleep)
    _require_dialog_closed(composer_driver, window_id, sleep)
    return DialogOutcome.SUBMITTED


def _move_to_last_question(composer_driver: ComposerDriver, window_id: WindowId, sleep: Callable[[float], None]) -> int:
    question_number, question_count = _open_question_position(composer_driver, window_id, sleep)
    for _ in range(question_count):
        if question_number >= question_count:
            break
        composer_driver.send_key(window_id, "right")
        screen, moved = poll(
            composer_driver,
            window_id,
            partial(_question_moved, previous_question_number=question_number),
            STEP_TIMEOUT_SECONDS,
            sleep,
        )
        if not moved:
            msg = "navigate"
            raise CodexAskError(msg, f"dialog did not move past question {question_number}")
        question_number = (current_question(screen) or (question_number,))[0]
    if question_number != question_count:
        msg = "navigate"
        raise CodexAskError(msg, f"never reached question {question_count} of {question_count}")
    return question_count


def _open_question_position(
    composer_driver: ComposerDriver,
    window_id: WindowId,
    sleep: Callable[[float], None],
) -> tuple[int, int]:
    screen, opened = poll(composer_driver, window_id, dialog_open, STEP_TIMEOUT_SECONDS, sleep)
    if not opened:
        msg = "open"
        raise CodexAskError(msg, "no question dialog on screen")
    position = current_question(screen)
    if position is None:
        msg = "question"
        raise CodexAskError(msg, "no current question on screen")
    return position


def _question_moved(screen: str, previous_question_number: int) -> bool:
    position = current_question(screen)
    return position is not None and position[0] != previous_question_number


def _dialog_closed(screen: str) -> bool:
    return not dialog_open(screen)


def _require_dialog_closed(
    composer_driver: ComposerDriver, window_id: WindowId, sleep: Callable[[float], None],
) -> None:
    _, closed = poll(composer_driver, window_id, _dialog_closed, STEP_TIMEOUT_SECONDS, sleep)
    if not closed:
        msg = "submit"
        raise CodexAskError(msg, "question dialog stayed open after decline")
