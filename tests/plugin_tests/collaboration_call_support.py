# Copyright (c) 2026 Zhambyl Yermagambet
"""Support for collaboration call tests."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from domain import (
    event_actor,
    event_conversation,
    ids as domain_ids,
)
from tests.plugin_tests import vocabulary as fixture
from tests.plugin_tests.collaboration_values import (
    COLLABORATION_CALLS,
    CodexRolloutTranslator,
    CollaborationArguments,
)
from tests.plugin_tests.support_events import payloads
from tests.plugin_tests.support_values import JsonValue, text_of

if TYPE_CHECKING:
    from pathlib import Path

    from harness.models.raw_events import (
        TranslationResult,
    )


def assert_child_assignment_start(
    payload: event_actor.ActorAssignmentStarted,
) -> None:
    """Verify the child assignment start payload."""
    assert str(payload.assignment_id) == fixture.CHILD_TURN_ID
    assert text_of(payload.brief) == "bali weather"
    assert payload.actor_name == "bali weather"
    assert payload.prompt is None


def assert_child_assignment_finish(
    payload: event_actor.ActorAssignmentFinished,
    translation: TranslationResult,
) -> None:
    """Verify the child assignment finish payload."""
    assert str(payload.assignment_id) == fixture.CHILD_TURN_ID
    assert text_of(payload.result) == "Rain, 24°C"
    assert not payloads(translation, event_actor.ActorFinished)


def collaboration_call_document(
    call_id: str,
    name: str,
    arguments: CollaborationArguments,
) -> dict[str, JsonValue]:
    """Build a native collaboration call document.

    Returns:
        The response-item document with JSON-encoded call arguments.

    """
    return {
        fixture.TYPE_FIELD: fixture.RESPONSE_ITEM,
        fixture.PAYLOAD_FIELD: {
            fixture.TYPE_FIELD: fixture.FUNCTION_CALL_ID,
            fixture.NAME_FIELD: name,
            fixture.ARGUMENTS_FIELD: json.dumps(arguments),
            fixture.CALL_ID_FIELD: call_id,
        },
    }


def write_collaboration_calls(rollout_path: Path) -> None:
    """Write the fixed collaboration calls as newline-separated JSON records."""
    rollout_path.write_text(
        "".join(
            f"{json.dumps(collaboration_call_document(call_id, name, arguments))}\n"
            for call_id, name, arguments in COLLABORATION_CALLS
        ), encoding="utf-8",
    )


def assert_collaboration_calls_ignored(translate_rollout: CodexRolloutTranslator) -> None:
    """Check that each collaboration call is marked as nonsemantic."""
    for call_id, name, arguments in COLLABORATION_CALLS:
        result = translate_rollout(
            collaboration_call_document(call_id, name, arguments),
            f"{call_id}-call",
        )
        assert result.canonical_events == ()
        assert result.decision == fixture.IGNORED_NONSEMANTIC


def assert_sent_collaboration_message(translate_rollout: CodexRolloutTranslator) -> None:
    """Check the recipient, role, and text of a translated collaboration message."""
    sent = translate_rollout(
        {
            fixture.TYPE_FIELD: fixture.EVENT_MSG_ID,
            fixture.PAYLOAD_FIELD: {
                fixture.TYPE_FIELD: fixture.ITEM_COMPLETED,
                fixture.TURN_ID_FIELD: fixture.LEAD_TURN_ID,
                fixture.ITEM_FIELD: {
                    fixture.TYPE_FIELD: fixture.SUBAGENT_ACTIVITY_KIND,
                    fixture.ID_FIELD: "send",
                    fixture.KIND_FIELD: "interacted",
                    fixture.AGENT_THREAD_ID_FIELD: fixture.CHILD_ONE_ID,
                    fixture.AGENT_PATH_FIELD: fixture.ROOT_WEATHER_PATH,
                },
            },
        },
        "send-activity",
    )
    message = payloads(sent, event_conversation.MessageCreated)[0].payload
    assert message.recipient_actor_id == domain_ids.ActorId(fixture.CHILD_ONE_ID)
    assert message.role == fixture.ASSISTANT
    assert text_of(message.content) == fixture.ENCRYPTED
