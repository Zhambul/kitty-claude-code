# Copyright (c) 2026 Zhambyl Yermagambet
"""Read tool call headers before parsing their arguments."""

from harness.impl.codex.canonical.record_rollout_headers import PayloadTypeHeader, RolloutDocument
from harness.impl.codex.ids_session_types import CodexCallId


class ToolCallHeader(PayloadTypeHeader):
    """Read a call identity without parsing its arguments."""

    call_id: CodexCallId | None = None


class ToolCallHeaderDocument(RolloutDocument[ToolCallHeader]):
    """Read the fields needed to select a recovery record."""
