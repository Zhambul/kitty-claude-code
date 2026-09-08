# Copyright (c) 2026 Zhambyl Yermagambet
"""Harness-specific prompt conventions used by the live question matrix."""

from tests.e2e.testkit.question_states import choice_label_matches
from tests.e2e.testkit.questions import native_question_prompt
from tests.e2e.testkit.references import SessionSpec


def test_codex_question_prompt_explains_native() -> None:
    """Verify codex question prompt explains the native free text wrapper."""
    prompt = native_question_prompt(
        SessionSpec("codex", "gpt-5.6-luna", "low"),
        "After the user answers, reply only with the exact answer text.",
    )

    assert "text after user_note:" in prompt
    assert "never include user_note: or None of the above" in prompt
    assert prompt.endswith("reply only with the exact answer text.")


def test_choice_label_matcher_tolerates_only() -> None:
    """Verify choice label matcher tolerates only the native recommendation badge."""
    expected_choice = "Blue"
    assert choice_label_matches(expected_choice, expected_choice)
    assert choice_label_matches(f"{expected_choice} (Recommended)", expected_choice)
    assert not choice_label_matches(f"Recommended: {expected_choice}", expected_choice)
    assert not choice_label_matches("Green (Recommended)", expected_choice)
