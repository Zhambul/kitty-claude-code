# Copyright (c) 2026 Zhambyl Yermagambet
"""Identify the visible Claude Code question."""

from dataclasses import dataclass

from harness.impl.claude_code.canonical.records import Question


@dataclass(frozen=True)
class QuestionMatch:
    """Describe the match strength for one question."""

    count: int
    question_index: int


def text_match(flat_screen: str, question: Question, question_index: int) -> QuestionMatch | None:
    """Return one question text match.

    Returns:
        The text length and question index, or None.

    """
    question_text = "".join((question.question or "").split())
    if not question_text or question_text not in flat_screen:
        return None
    return QuestionMatch(len(question_text), question_index)


def longest_text_match(visible_region: str, questions: list[Question]) -> int | None:
    """Return the index of the longest matching question text.

    Returns:
        The matching question index, or None.

    """
    flat_screen = "".join(visible_region.split())
    best_match = QuestionMatch(0, -1)
    for question_index, question in enumerate(questions):
        candidate = text_match(flat_screen, question, question_index)
        if candidate is not None and candidate.count > best_match.count:
            best_match = candidate
    return None if best_match.question_index < 0 else best_match.question_index


def option_match(visible_labels: set[str], question: Question, question_index: int) -> QuestionMatch:
    """Return the visible option count for one question.

    Returns:
        The option count and question index.

    """
    option_labels: set[str] = set()
    for option in question.options or ():
        label = (option.label or "").strip()
        if label:
            option_labels.add(label)
    return QuestionMatch(len(visible_labels & option_labels), question_index)


def best_unique_match(matches: list[QuestionMatch]) -> int | None:
    """Return the index of one unique best option match.

    Returns:
        The unique best question index, or None.

    """
    best_count = 0
    best_index: int | None = None
    tied = False
    for question_match in matches:
        if question_match.count > best_count:
            best_count = question_match.count
            best_index = question_match.question_index
            tied = False
        elif question_match.count == best_count and question_match.count > 0:
            tied = True
    return None if tied else best_index


def unique_option_match(visible_labels: set[str], questions: list[Question]) -> int | None:
    """Return the question with one unique best option match.

    Returns:
        The unique question index, or None.

    """
    matches: list[QuestionMatch] = []
    for question_index, question in enumerate(questions):
        matches.append(option_match(visible_labels, question, question_index))
    return best_unique_match(matches)


def current_question(visible_region: str, visible_labels: set[str], questions: list[Question]) -> int | None:
    """Return the question that the dialog shows.

    Returns:
        The visible question index, or None.

    """
    question_index = longest_text_match(visible_region, questions)
    if question_index is not None:
        return question_index
    return unique_option_match(visible_labels, questions)
