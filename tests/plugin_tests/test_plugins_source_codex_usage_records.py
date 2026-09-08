# Copyright (c) 2026 Zhambyl Yermagambet
"""Check the additional records from Codex 0.153.4."""

import pytest
from pydantic import ValidationError

from harness.impl.codex.canonical import rollout
from harness.impl.codex.canonical.record_interaction_records import SettingsRecord
from harness.impl.codex.canonical.record_terminal_records import EmptyRecord
from harness.impl.codex.model import CodexEffort, CodexModel
from tests.plugin_tests import vocabulary as fixture


def test_thread_settings_accepts_thread_identity() -> None:
    """Keep model selections when the event includes its thread ID."""
    record = rollout.parse({
        fixture.TYPE_FIELD: "event_msg",
        "payload": {
            fixture.TYPE_FIELD: "thread_settings_applied",
            "thread_id": "thread-one",
            "thread_settings": {"model": "gpt-5.6-luna", "reasoning_effort": "low"},
        },
    })

    assert isinstance(record, SettingsRecord)
    assert record.model is CodexModel.GPT_FIVE_SIX_LUNA
    assert record.effort is CodexEffort.LOW


def test_usage_record_has_no_duplicate_counts() -> None:
    """Validate usage details without a second canonical usage record."""
    record = rollout.parse({
        fixture.TYPE_FIELD: "token_usage_record",
        "payload": {
            "thread_id": "thread-one",
            "turn_id": "turn-one",
            "session_id": "session-one",
            "root_turn_id": "root-turn",
            "response_id": "response-one",
            "usage": {"input_tokens": 12479, "output_tokens": 77, "total_tokens": 12556},
            "turn_token_usage": {"input_tokens": 12479, "output_tokens": 77, "total_tokens": 12556},
            "thread_token_usage": {"input_tokens": 12479, "output_tokens": 77, "total_tokens": 12556},
        },
    })

    assert isinstance(record, EmptyRecord)


def test_incomplete_usage_record_is_rejected() -> None:
    """Do not accept a record with missing usage details."""
    with pytest.raises(ValidationError, match="thread_token_usage"):
        rollout.parse({fixture.TYPE_FIELD: "token_usage_record", "payload": {}})
