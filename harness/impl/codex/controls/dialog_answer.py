# Copyright (c) 2026 Zhambyl Yermagambet
"""Answer questions in the Codex dialog."""

import time
from collections.abc import Callable

from domain.ids import WindowId
from harness.contract import ComposerDriver
from harness.impl.codex.controls.dialog_models import Answer, CodexAskError, DialogOutcome, Prompt, QuestionSet
from harness.impl.codex.controls.dialog_navigation import STEP_TIMEOUT_SECONDS, add_note, cursor_to
from harness.impl.codex.controls.dialog_screen_rows import NONE_LABEL, none_row, row_number
from harness.impl.codex.controls.dialog_screen_state import (
    confirm_open,
    confirmation_closed,
    current_question,
    dialog_open,
    poll,
    screen_text,
)

PROCEED_LABEL = "Proceed"


def _answer_one(
    composer_driver: ComposerDriver,
    window_id: WindowId,
    prompt: Prompt,
    answer: Answer,
    sleep: Callable[[float], None],
) -> None:
    other = answer.other.strip()
    row = _answer_row(composer_driver, window_id, prompt, answer, other)
    cursor_to(composer_driver, window_id, row, sleep)
    if other:
        add_note(composer_driver, window_id, other, sleep)
        return
    composer_driver.send_key(window_id, "enter")


def _answer_row(
    composer_driver: ComposerDriver, window_id: WindowId, prompt: Prompt, answer: Answer, other: str,
) -> str:
    labels = [option.label for option in prompt.options]
    selected = next((selection for selection in answer.selected if selection in labels), None)
    if selected is not None:
        return str(1 + labels.index(selected))
    if other:
        row = none_row(screen_text(composer_driver, window_id), prompt)
        if row:
            return row
        msg = "noneof"
        raise CodexAskError(msg, f"no {NONE_LABEL!r} row for a free-text answer")
    question_preview = prompt.question[:60]
    msg = "options"
    raise CodexAskError(msg, f"no answer for {question_preview!r}")


def _confirm(composer_driver: ComposerDriver, window_id: WindowId, sleep: Callable[[float], None]) -> None:
    screen = screen_text(composer_driver, window_id)
    if not confirm_open(screen):
        return
    cursor_to(composer_driver, window_id, row_number(screen, PROCEED_LABEL) or "1", sleep)
    composer_driver.send_key(window_id, "enter")
    _, closed = poll(composer_driver, window_id, confirmation_closed, STEP_TIMEOUT_SECONDS, sleep)
    if not closed:
        msg = "confirm"
        raise CodexAskError(msg, "the unanswered-questions confirm stayed up")


def drive(
    composer_driver: ComposerDriver,
    window_id: WindowId,
    questions: list[Prompt],
    answers: list[Answer],
    sleep: Callable[[float], None] = time.sleep,
) -> DialogOutcome:
    """Answer all visible Codex questions.

    Returns:
        The submitted dialog outcome after the answer sequence completes.

    Raises:
        CodexAskError: If the dialog is absent or the answer count does not match the question count.

    """
    _, opened = poll(composer_driver, window_id, dialog_open, STEP_TIMEOUT_SECONDS, sleep)
    if not opened:
        msg = "open"
        raise CodexAskError(msg, "no question dialog on screen")
    if len(answers) != len(questions):
        msg = "answers"
        raise CodexAskError(msg, f"expected {len(questions)} answers, got {len(answers)}")
    question_set = QuestionSet(questions, answers)
    last_question_index = -1
    for _ in range(len(questions) + 1):
        screen = screen_text(composer_driver, window_id)
        if confirm_open(screen) or not dialog_open(screen):
            break
        last_question_index = _answer_visible_question(
            composer_driver, window_id, question_set, last_question_index, sleep,
        )
    _confirm(composer_driver, window_id, sleep)
    return DialogOutcome.SUBMITTED


def _answer_visible_question(
    composer_driver: ComposerDriver,
    window_id: WindowId,
    question_set: QuestionSet,
    last_question_index: int,
    sleep: Callable[[float], None],
) -> int:
    position = current_question(screen_text(composer_driver, window_id))
    if position is None:
        msg = "question"
        raise CodexAskError(msg, "no current question on screen")
    question_index = position[0] - 1
    if question_index <= last_question_index:
        msg = "advance"
        raise CodexAskError(msg, f"dialog did not advance past question {position[0]}")
    if not 0 <= question_index < len(question_set.answers):
        msg = "answers"
        raise CodexAskError(msg, f"no answer for question {position[0]}")
    _answer_one(
        composer_driver, window_id, question_set.questions[question_index], question_set.answers[question_index], sleep,
    )
    _require_question_advance(composer_driver, window_id, position[0], sleep)
    return question_index


def _require_question_advance(
    composer_driver: ComposerDriver,
    window_id: WindowId,
    question_number: int,
    sleep: Callable[[float], None],
) -> None:
    _, advanced = poll(
        composer_driver,
        window_id,
        lambda screen: _answer_landed(screen, question_number),
        STEP_TIMEOUT_SECONDS,
        sleep,
    )
    if not advanced:
        msg = "advance"
        raise CodexAskError(msg, f"dialog did not advance past question {question_number}")


def _answer_landed(screen: str, expected_question_number: int) -> bool:
    position = current_question(screen)
    if position is None:
        return True
    if position[0] != expected_question_number:
        return True
    return not dialog_open(screen) or confirm_open(screen)
