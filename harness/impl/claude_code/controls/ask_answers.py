# Copyright (c) 2026 Zhambyl Yermagambet
"""Apply answers to Claude Code question dialog rows."""

from harness.impl.claude_code.controls import (
    ask_navigation,
    ask_option_selection,
    askdialog_screen as ask_screen,
    screen_driver as screen_actions,
)
from harness.impl.claude_code.controls.ask_models import AnswerDraft, AskContext, AskError

STEP_TIMEOUT_SECONDS = 2.5


def advance_multiple_choice(ask_context: AskContext, question_index: int) -> None:
    """Advance one multiple-choice question.

    Raises:
        AskError: If the dialog does not advance.

    """
    ask_navigation.cursor_to(ask_context, lambda row: row.label in {"Next", "Submit"}, "advance row")
    ask_context.screen_driver.send_key(ask_context.window_id, "enter")
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
        raise AskError(
            message,
            f"multiple choice did not advance past question {question_number}",
            screen=screen,
        )


def answer_multiple_choice(
    ask_context: AskContext,
    question_index: int,
    labels: list[str],
    selected_labels: list[str],
    other_text: str,
) -> None:
    """Apply one multiple-choice answer and advance."""
    ask_option_selection.toggle_options(ask_context, labels, selected_labels)
    if other_text:
        text_row_digit = str(len(labels) + 1)
        ask_option_selection.enter_other(ask_context, other_text, text_row_digit, verify_check=True)
    advance_multiple_choice(ask_context, question_index)


def answer_single_choice(
    ask_context: AskContext,
    question_index: int,
    labels: list[str],
    selected_labels: list[str],
    other_text: str,
) -> None:
    """Apply one single-choice answer.

    Raises:
        AskError: If no answer is present.

    """
    if other_text:
        text_row_digit = str(len(labels) + 1)
        ask_option_selection.enter_other(ask_context, other_text, text_row_digit, verify_check=False)
        return
    if not selected_labels:
        question_text = ask_context.questions[question_index].question or ""
        message = "options"
        question_preview = question_text[:60]
        raise AskError(message, f"no answer for {question_preview!r}")
    selected_digit = str(labels.index(selected_labels[0]) + 1)
    ask_navigation.cursor_to(ask_context, ask_navigation.digit_matches(selected_digit), f"option {selected_digit}")
    ask_context.screen_driver.send_key(ask_context.window_id, "enter")


def answer_question(ask_context: AskContext, question_index: int, answer_draft: AnswerDraft) -> None:
    """Apply one answer to the current question."""
    question = ask_context.questions[question_index]
    labels = [option.label or "" for option in (question.options or [])]
    selected_labels = [label for label in (answer_draft.selected or []) if label in labels]
    other_text = (answer_draft.other or "").strip()
    if question.multi_select:
        answer_multiple_choice(ask_context, question_index, labels, selected_labels, other_text)
        return
    answer_single_choice(ask_context, question_index, labels, selected_labels, other_text)
