# Copyright (c) 2026 Zhambyl Yermagambet
"""Read Codex usage documents."""

from typing import Literal

from harness.impl.codex.canonical.record_rollout_headers import RolloutDocument
from harness.impl.codex.canonical.record_usage_payloads import TokenUsageRecordPayload


class TokenUsageDocument(RolloutDocument[TokenUsageRecordPayload]):
    """Read a token usage record."""

    type: Literal["token_usage_record"] = "token_usage_record"
