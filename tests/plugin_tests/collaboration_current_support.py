# Copyright (c) 2026 Zhambyl Yermagambet
"""Support for current collaboration tests."""

import json
from functools import partial
from pathlib import Path

import pytest
from pydantic import ValidationError

from domain import (
    event_shell,
    outcomes,
)
from harness.impl.codex.canonical import rollout as codex_rollout
from harness.impl.codex.canonical.translator import CodexCanonicalTranslator
from harness.models.raw_events import (
    TranslationResult,
)
from tests.plugin_tests import (
    collaboration_assertion_support,
    collaboration_lifecycle_support,
    collaboration_values,
    support_events,
    support_values,
    vocabulary as fixture,
)


def current_collaboration_translator(tmp_path: Path) -> collaboration_values.CodexPositionedRolloutTranslator:
    """Create a Codex translator bound to an empty test rollout.

    Returns:
        The translation function with the translator and rollout path supplied.

    """
    rollout_path = tmp_path / "lead.jsonl"
    rollout_path.write_text("")
    translator = CodexCanonicalTranslator()
    return partial(collaboration_lifecycle_support.translate_codex_rollout_from_path, translator, rollout_path)


def assert_current_collaboration_item(
    translate_rollout: collaboration_values.CodexPositionedRolloutTranslator,
    call_id: str,
) -> None:
    """Check that a known collaboration item is ignored and unknown fields are rejected."""
    item_payload: dict[str, support_values.JsonValue] = {
        fixture.TYPE_FIELD: "CollabAgentToolCall",
        fixture.ID_FIELD: call_id,
        fixture.TOOL_KIND: "spawn_agent",
        fixture.STATUS_FIELD: fixture.COMPLETED,
        "sender_thread_id": fixture.LEAD_ONE_ID,
        "receiver_thread_ids": [fixture.CHILD_ONE_ID],
        "receiver_agents": [{fixture.THREAD_ID_FIELD: fixture.CHILD_ONE_ID, "agent_nickname": "Dirac"}],
        fixture.PROMPT_KIND: "reply only with the word gathered.",
        fixture.MODEL: fixture.GPT_FIVE_SIX_LUNA,
        "reasoning_effort": "low",
        "agents_states": {fixture.CHILD_ONE_ID: "pending_init"},
    }
    item_document: dict[str, support_values.JsonValue] = {
        fixture.TYPE_FIELD: fixture.EVENT_MSG_ID,
        fixture.PAYLOAD_FIELD: {
            fixture.TYPE_FIELD: fixture.ITEM_COMPLETED,
            fixture.TURN_ID_FIELD: fixture.LEAD_TURN_ID,
            "started_at_ms": 1000,
            "completed_at_ms": 2000,
            fixture.THREAD_ID_FIELD: fixture.LEAD_ONE_ID,
            fixture.ITEM_FIELD: item_payload,
        },
    }
    collaboration_assertion_support.assert_ignored_translation(translate_rollout(item_document, "spawn-item", "30"))
    item_payload["unmeasured_field"] = True
    with pytest.raises(ValidationError):
        codex_rollout.parse_line(json.dumps(item_document))


def assert_yielded_shell(
    translation: TranslationResult,
    shell: event_shell.ShellStarted,
) -> None:
    """Verify that yielded output backgrounds the active shell."""
    assert support_events.payloads(translation, event_shell.ShellBackgrounded)[0].payload.shell_id == shell.shell_id
    assert support_events.payloads(translation, event_shell.ShellFinished) == []
    assert support_events.payloads(translation, event_shell.ShellProgressed) == []


def assert_completed_shell(
    translation: TranslationResult,
    shell: event_shell.ShellStarted,
) -> None:
    """Verify that the completed item finishes the active shell."""
    finished = support_events.payloads(translation, event_shell.ShellFinished)[0].payload
    assert finished.shell_id == shell.shell_id
    assert finished.outcome == outcomes.Outcome.SUCCEEDED
    assert support_events.payloads(translation, event_shell.ShellOutputFinished)[0].payload.shell_id == shell.shell_id
