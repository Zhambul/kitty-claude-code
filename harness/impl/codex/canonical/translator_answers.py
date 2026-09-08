# Copyright (c) 2026 Zhambyl Yermagambet
"""Split Codex canonical translation."""

from __future__ import annotations

from harness.impl.codex.canonical import translator_dependencies as dependencies


def _canonical_question_answer(
    document: dependencies.record_payload_namespaces.record_plan_arguments.AskResultDocument,
    native_question_id: dependencies.translator_id_dependencies.ids_conversation_types.CodexQuestionId,
) -> dependencies.translator_domain_events.attention.AttentionAnswer:
    answer = document.answers.root.get(native_question_id)
    if answer is None:
        msg = f"Codex question result has no answer for {native_question_id!r}"
        raise dependencies.translator_service_dependencies.raw_events.TranslationError(
            msg,
        )
    return dependencies.translator_domain_events.attention.AttentionAnswer(
        dependencies.translator_id_dependencies.ids_conversation.question_id_from_codex(
            dependencies.translator_id_dependencies.ids_conversation_types.CodexQuestionId(native_question_id),
        ),
        _question_answer_labels(answer.answers),
    )


def _question_answers(
    ask_record: dependencies.record_canonical_namespaces.record_interaction_records.AskRecord,
    document: dependencies.record_payload_namespaces.record_plan_arguments.AskResultDocument,
) -> tuple[dependencies.translator_domain_events.attention.AttentionAnswer, ...]:
    return tuple(
        _canonical_question_answer(
            document,
            dependencies.translator_id_dependencies.ids_conversation_types.CodexQuestionId(question.id or str(index)),
        )
        for index, question in enumerate(ask_record.questions)
    )


def _question_answer_labels(native_labels: tuple[str, ...]) -> tuple[str, ...]:
    """Remove Codex dialog controls from one canonical question answer.

    Returns:
        Result items.

    """
    note = _question_note(native_labels)
    if not note:
        return native_labels
    selected = tuple(label for label in native_labels if _is_selected_answer(label))
    return (*selected, note)


def _question_note(native_labels: tuple[str, ...]) -> str:
    note_prefix = "user_note:"
    for label in native_labels:
        if label.casefold().startswith(note_prefix):
            return label[len(note_prefix) :].strip()
    return ""


def _is_selected_answer(label: str) -> bool:
    if label == "None of the above":
        return False
    return not label.casefold().startswith("user_note:")
