# Copyright (c) 2026 Zhambyl Yermagambet
"""Convert Claude Code call identifiers."""

from domain import ids as domain_ids
from harness.impl.claude_code.id_session_types import ClaudeCodeCallId


def skill_id_from_claude_code_call(claude_code_call_id: ClaudeCodeCallId) -> domain_ids.SkillId:
    """Return the domain skill identifier.

    Returns:
        The domain skill identifier.

    """
    return domain_ids.SkillId(claude_code_call_id)


def assignment_id_from_claude_code_call(claude_code_call_id: ClaudeCodeCallId) -> domain_ids.AssignmentId:
    """Return the domain assignment identifier.

    Returns:
        The domain assignment identifier.

    """
    return domain_ids.AssignmentId(claude_code_call_id)


def attention_id_from_claude_code_call(claude_code_call_id: ClaudeCodeCallId) -> domain_ids.AttentionId:
    """Return the domain attention identifier.

    Returns:
        The domain attention identifier.

    """
    return domain_ids.AttentionId(claude_code_call_id)


def message_id_from_claude_code_call(claude_code_call_id: ClaudeCodeCallId) -> domain_ids.MessageId:
    """Return the domain message identifier.

    Returns:
        The domain message identifier.

    """
    return domain_ids.MessageId(claude_code_call_id)
