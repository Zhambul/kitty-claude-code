# Copyright (c) 2026 Zhambyl Yermagambet
"""Convert Claude Code session identifiers."""

from domain import ids as domain_ids
from harness.impl.claude_code.id_session_types import ClaudeCodeActorId, ClaudeCodeCallId, ClaudeCodeSessionId


def session_id_from_claude_code(claude_code_session_id: ClaudeCodeSessionId) -> domain_ids.SessionId:
    """Return the domain session identifier.

    Returns:
        The domain session identifier.

    """
    return domain_ids.SessionId(claude_code_session_id)


def claude_code_session_id_from_domain(session_id: domain_ids.SessionId) -> ClaudeCodeSessionId:
    """Return the native session identifier.

    Returns:
        The native session identifier.

    """
    return ClaudeCodeSessionId(session_id)


def actor_id_from_claude_code(claude_code_actor_id: ClaudeCodeActorId) -> domain_ids.ActorId:
    """Return the domain actor identifier.

    Returns:
        The domain actor identifier.

    """
    return domain_ids.ActorId(claude_code_actor_id)


def lead_actor_id_from_claude_code(claude_code_session_id: ClaudeCodeSessionId) -> domain_ids.ActorId:
    """Return the domain lead actor identifier.

    Returns:
        The domain lead actor identifier.

    """
    return domain_ids.ActorId(f"{claude_code_session_id}:lead")


def shell_id_from_claude_code_call(claude_code_call_id: ClaudeCodeCallId) -> domain_ids.ShellId:
    """Return the domain shell identifier.

    Returns:
        The domain shell identifier.

    """
    return domain_ids.ShellId(claude_code_call_id)
