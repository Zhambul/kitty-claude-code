# Copyright (c) 2026 Zhambyl Yermagambet
"""Convert Codex session identifiers to domain identifiers."""

from domain import ids as domain_ids
from harness.impl.codex.ids_session_types import CodexActorId, CodexCallId, CodexSessionId


def session_id_from_codex(codex_session_id: CodexSessionId) -> domain_ids.SessionId:
    """Return the domain session identifier.

    Returns:
        The domain session identifier.

    """
    return domain_ids.SessionId(codex_session_id)


def codex_session_id_from_domain(session_id: domain_ids.SessionId) -> CodexSessionId:
    """Return the native session identifier.

    Returns:
        The native session identifier.

    """
    return CodexSessionId(session_id)


def actor_id_from_codex(codex_actor_id: CodexActorId) -> domain_ids.ActorId:
    """Return the domain actor identifier.

    Returns:
        The domain actor identifier.

    """
    return domain_ids.ActorId(codex_actor_id)


def lead_actor_id_from_codex(codex_session_id: CodexSessionId) -> domain_ids.ActorId:
    """Return the domain lead actor identifier.

    Returns:
        The domain lead actor identifier.

    """
    return domain_ids.ActorId(f"{codex_session_id}:lead")


def shell_id_from_codex_call(codex_call_id: CodexCallId) -> domain_ids.ShellId:
    """Return the domain shell identifier.

    Returns:
        The domain shell identifier.

    """
    return domain_ids.ShellId(codex_call_id)
