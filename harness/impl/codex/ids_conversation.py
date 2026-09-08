# Copyright (c) 2026 Zhambyl Yermagambet
"""Convert Codex conversation identifiers to domain identifiers."""

from domain import ids as domain_ids
from harness.impl.codex.ids_conversation_types import (
    CodexMessageId,
    CodexQuestionId,
    CodexReasoningId,
    CodexTurnId,
)
from harness.impl.codex.ids_session_types import CodexCallId


def attention_id_from_codex_call(codex_call_id: CodexCallId) -> domain_ids.AttentionId:
    """Return the domain attention identifier from a call.

    Returns:
        The domain attention identifier from a call.

    """
    return domain_ids.AttentionId(codex_call_id)


def message_id_from_codex_call(codex_call_id: CodexCallId) -> domain_ids.MessageId:
    """Return the domain message identifier from a call.

    Returns:
        The domain message identifier from a call.

    """
    return domain_ids.MessageId(codex_call_id)


def message_id_from_codex(codex_message_id: CodexMessageId) -> domain_ids.MessageId:
    """Return the domain message identifier.

    Returns:
        The domain message identifier.

    """
    return domain_ids.MessageId(codex_message_id)


def reasoning_id_from_codex(codex_reasoning_id: CodexReasoningId) -> domain_ids.ReasoningId:
    """Return the domain reasoning identifier.

    Returns:
        The domain reasoning identifier.

    """
    return domain_ids.ReasoningId(codex_reasoning_id)


def turn_id_from_codex(codex_turn_id: CodexTurnId) -> domain_ids.TurnId:
    """Return the domain turn identifier.

    Returns:
        The domain turn identifier.

    """
    return domain_ids.TurnId(codex_turn_id)


def assignment_id_from_codex_turn(codex_turn_id: CodexTurnId) -> domain_ids.AssignmentId:
    """Return the domain assignment identifier.

    Returns:
        The domain assignment identifier.

    """
    return domain_ids.AssignmentId(codex_turn_id)


def question_id_from_codex(codex_question_id: CodexQuestionId) -> domain_ids.QuestionId:
    """Return the domain question identifier.

    Returns:
        The domain question identifier.

    """
    return domain_ids.QuestionId(codex_question_id)
