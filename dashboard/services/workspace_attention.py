# Copyright (c) 2026 Zhambyl Yermagambet
"""Extract pending question data from session entries."""

from collections.abc import Mapping

from domain.attention import AttentionPrompt
from domain.entries import SessionEntry
from domain.entry_attention import QuestionAskedBody
from domain.ids import AttentionId


def pending_questions(
    pending_attention: tuple[SessionEntry, ...],
) -> Mapping[AttentionId, tuple[AttentionPrompt, ...]]:
    """Return pending questions by attention identifier.

    Returns:
        Pending questions by attention identifier.

    """
    return {
        entry.body.attention_id: entry.body.questions
        for entry in pending_attention
        if isinstance(entry.body, QuestionAskedBody)
    }
