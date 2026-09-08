# Copyright (c) 2026 Zhambyl Yermagambet
"""Support for collaboration activity tests."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tests.plugin_tests import vocabulary as fixture

if TYPE_CHECKING:
    from tests.plugin_tests.collaboration_values import CodexRolloutTranslator


def assert_nonsemantic_collaboration_activities(translate_rollout: CodexRolloutTranslator) -> None:
    """Check that control activity records create no canonical events."""
    for call_id, activity in (
        ("spawn", fixture.STARTED),
        ("follow", "interacted"),
        (fixture.INTERRUPT, fixture.INTERRUPTED),
    ):
        result = translate_rollout(
            {
                fixture.TYPE_FIELD: fixture.EVENT_MSG_ID,
                fixture.PAYLOAD_FIELD: {
                    fixture.TYPE_FIELD: fixture.ITEM_COMPLETED,
                    fixture.TURN_ID_FIELD: fixture.LEAD_TURN_ID,
                    fixture.ITEM_FIELD: {
                        fixture.TYPE_FIELD: fixture.SUBAGENT_ACTIVITY_KIND,
                        fixture.ID_FIELD: call_id,
                        fixture.KIND_FIELD: activity,
                        fixture.AGENT_THREAD_ID_FIELD: fixture.CHILD_ONE_ID,
                        fixture.AGENT_PATH_FIELD: fixture.ROOT_WEATHER_PATH,
                    },
                },
            },
            f"{call_id}-activity",
        )
        assert result.canonical_events == ()
        assert result.decision == fixture.IGNORED_NONSEMANTIC


def assert_completed_activity_ignored(translate_rollout: CodexRolloutTranslator) -> None:
    """Check that a completed child activity record is ignored."""
    completed = translate_rollout(
        {
            fixture.TYPE_FIELD: fixture.EVENT_MSG_ID,
            fixture.PAYLOAD_FIELD: {
                fixture.TYPE_FIELD: fixture.ITEM_COMPLETED,
                fixture.TURN_ID_FIELD: fixture.LEAD_TURN_ID,
                fixture.ITEM_FIELD: {
                    fixture.TYPE_FIELD: fixture.SUBAGENT_ACTIVITY_KIND,
                    fixture.ID_FIELD: "subagent-completed-child-one",
                    fixture.KIND_FIELD: fixture.COMPLETED,
                    fixture.AGENT_THREAD_ID_FIELD: fixture.CHILD_ONE_ID,
                    fixture.AGENT_PATH_FIELD: fixture.ROOT_WEATHER_PATH,
                },
            },
        },
        "completed-activity",
    )
    assert completed.canonical_events == ()
    assert completed.decision == fixture.IGNORED_NONSEMANTIC


def assert_collaboration_outputs_ignored(translate_rollout: CodexRolloutTranslator) -> None:
    """Check that collaboration control results create no canonical events."""
    for call_id, output in (
        ("spawn", '{"task_name":"/root/weather"}'),
        ("follow", ""),
        ("wait", '{"message":"Wait timed out.","timed_out":true}'),
        (fixture.INTERRUPT, '{"previous_status":"running"}'),
        ("list", '{"agents":[]}'),
    ):
        result = translate_rollout(
            {
                fixture.TYPE_FIELD: fixture.RESPONSE_ITEM,
                fixture.PAYLOAD_FIELD: {
                    fixture.TYPE_FIELD: fixture.FUNCTION_CALL_OUTPUT_ID,
                    fixture.CALL_ID_FIELD: call_id,
                    fixture.OUTPUT_FIELD: output,
                },
            },
            f"{call_id}-output",
        )
        assert result.canonical_events == ()
        assert result.decision == fixture.IGNORED_NONSEMANTIC
