# Copyright (c) 2026 Zhambyl Yermagambet
"""Convert Codex attention identifiers to domain identifiers."""

from domain import ids as domain_ids
from harness.impl.codex.ids_conversation_types import CodexAttentionId


def attention_id_from_codex(codex_attention_id: CodexAttentionId) -> domain_ids.AttentionId:
    """Return the domain attention identifier.

    Returns:
        The domain attention identifier.

    """
    return domain_ids.AttentionId(codex_attention_id)
