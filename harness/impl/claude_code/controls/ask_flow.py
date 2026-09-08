# Copyright (c) 2026 Zhambyl Yermagambet
"""Run the verified phases of a Claude Code question dialog."""

from harness.impl.claude_code.controls import (
    ask_answers,
    ask_navigation,
    ask_review,
    askdialog_screen as ask_screen,
    screen_driver as screen_actions,
)
from harness.impl.claude_code.controls.ask_models import AnswerDraft, AskContext, AskError, AskOutcome
from harness.impl.claude_code.controls.askdialog_screen import CHAT_LABEL

STEP_TIMEOUT_SECONDS = 2.5


def open_dialog(ask_context: AskContext) -> str:
    """Wait for the question dialog.

    Returns:
        The open dialog screen.

    Raises:
        AskError: If no dialog appears.

    """
    screen, opened = screen_actions.poll_until(
        ask_context.screen_driver,
        ask_context.window_id,
        lambda current_screen: ask_screen.dialog_open(current_screen) or ask_screen.review_open(current_screen),
        STEP_TIMEOUT_SECONDS,
        ask_context.sleep,
    )
    if not opened:
        message = "open"
        raise AskError(message, "no question dialog is on screen", screen=screen)
    return screen


def choose_chat(ask_context: AskContext, screen: str) -> AskOutcome:
    """Choose the Chat about this row.

    Returns:
        The chat outcome.

    Raises:
        AskError: If the chat row is absent or the dialog stays open.

    """
    if not any(row.label == CHAT_LABEL for row in ask_screen.rows(screen)):
        message = "chat"
        raise AskError(message, "no Chat about this row is on screen")
    ask_navigation.cursor_to(ask_context, lambda row: row.label == CHAT_LABEL, "Chat row")
    ask_context.screen_driver.send_key(ask_context.window_id, "enter")
    _screen, closed = screen_actions.poll_until(
        ask_context.screen_driver,
        ask_context.window_id,
        lambda current_screen: (
            not ask_screen.dialog_open(current_screen) and not ask_screen.review_open(current_screen)
        ),
        STEP_TIMEOUT_SECONDS,
        ask_context.sleep,
    )
    if not closed:
        message = "chat"
        raise AskError(message, "the dialog is still open")
    return AskOutcome.CHAT


def verify_answer_count(ask_context: AskContext, answers: list[AnswerDraft]) -> None:
    """Verify that each question has one answer.

    Raises:
        AskError: If the answer count is not correct.

    """
    if len(answers) != len(ask_context.questions):
        message = "answers"
        raise AskError(message, f"expected {len(ask_context.questions)} answers, got {len(answers)}")


def wait_for_advance(ask_context: AskContext, question_index: int) -> None:
    """Verify that one answer advances the dialog.

    Raises:
        AskError: If the dialog does not advance.

    """
    screen, advanced = screen_actions.poll_until(
        ask_context.screen_driver,
        ask_context.window_id,
        lambda current_screen: (
            ask_screen.current_question(current_screen, ask_context.questions) != question_index
            or ask_screen.review_open(current_screen)
            or not ask_screen.dialog_open(current_screen)
        ),
        STEP_TIMEOUT_SECONDS,
        ask_context.sleep,
    )
    if not advanced:
        question_number = question_index + 1
        message = "advance"
        raise AskError(message, f"dialog did not advance past question {question_number}", screen=screen)


def next_question_index(ask_context: AskContext, previous_question_index: int) -> int | None:
    """Return the next visible question index.

    Returns:
        The next index, or None when the question flow is complete.

    Raises:
        AskError: If the visible question is unknown or did not advance.

    """
    screen = ask_context.screen_driver.read_text(ask_context.window_id) or ""
    if ask_screen.review_open(screen) or not ask_screen.dialog_open(screen):
        return None
    question_index = ask_screen.current_question(screen, ask_context.questions)
    if question_index is None:
        message = "question"
        raise AskError(message, "no current question is on screen", screen=screen)
    if question_index <= previous_question_index:
        question_number = question_index + 1
        message = "advance"
        raise AskError(message, f"dialog did not advance past question {question_number}", screen=screen)
    return question_index


def answer_visible_questions(ask_context: AskContext, answers: list[AnswerDraft]) -> None:
    """Answer each remaining visible question in order."""
    previous_question_index = -1
    for _ in range(len(ask_context.questions) + 1):
        question_index = next_question_index(ask_context, previous_question_index)
        if question_index is None:
            return
        ask_answers.answer_question(ask_context, question_index, answers[question_index])
        wait_for_advance(ask_context, question_index)
        previous_question_index = question_index


def drive_dialog(ask_context: AskContext, answers: list[AnswerDraft], *, chat: bool = False) -> AskOutcome:
    """Drive one open Claude Code question dialog.

    Returns:
        The completed question dialog outcome.

    """
    screen = open_dialog(ask_context)
    if chat:
        return choose_chat(ask_context, screen)
    verify_answer_count(ask_context, answers)
    answer_visible_questions(ask_context, answers)
    ask_review.submit(ask_context, ask_review.wait_for_review_or_close(ask_context))
    return AskOutcome.SUBMITTED
