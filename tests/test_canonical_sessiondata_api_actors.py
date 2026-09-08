# Copyright (c) 2026 Zhambyl Yermagambet
"""Test canonical sessiondata api actors."""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal

import pytest

from api.sessiondata import mapper
from domain import (
    actor_state,
    ids as domain_ids,
    session_state,
    usage,
)
from tests import canonical_sessiondata_api_values as api_values


def test_actor_carries_one_model_name_and_never() -> None:
    """Verify an actor carries one model name and never the ids behind it.

    The picker gets its selectable ids from the harness catalog; a reader
        needs the name. The native id stays in the read model, where the relaunch
        path reads it.
    """
    response = mapper.actor(api_values.ACTOR)
    assert response.model == api_values.MODEL_DISPLAY_NAME
    assert response.effort == "high"
    assert response.status == "executing"
    assert "native_id" not in response.model_dump_json()


def test_an_actors_numbers_are_its_own() -> None:
    """Verify an actors numbers are its own."""
    response = mapper.actor(
        replace(
            api_values.ACTOR,
            usage=actor_state.ActorUsage(
                usage.TokenUsage(
                    input_tokens=api_values.ACTOR_INPUT_TOKENS, output_tokens=api_values.ACTOR_OUTPUT_TOKENS,
                ),
                Decimal("1.42"),
            ),
            context=actor_state.ActorContext(
                used_tokens=api_values.ACTOR_CONTEXT_USED_TOKENS,
                window_tokens=api_values.ACTOR_CONTEXT_WINDOW_TOKENS,
                compacting=False,
            ),
            statistics=actor_state.ActorStatistics(
                prompt_count=7,
                shell_command_count=api_values.SHELL_COMMAND_COUNT,
                failed_shell_command_count=1,
                file_count=4,
                lines_added=api_values.LINES_ADDED,
                lines_removed=api_values.LINES_REMOVED,
                actor_message_count=2,
                tool_counts=(
                    actor_state.ToolCount("Bash", api_values.SHELL_COMMAND_COUNT),
                    actor_state.ToolCount("Read", 4),
                ),
                active_seconds=api_values.ACTOR_ACTIVE_SECONDS,
            ),
        ),
    )

    assert response.usage.tokens.input_tokens == api_values.ACTOR_INPUT_TOKENS
    # A string, because money is a decimal and JSON has one number type.
    assert response.usage.cost_in_usd == "1.42"
    assert response.context.used_tokens == api_values.ACTOR_CONTEXT_USED_TOKENS
    assert {count.tool: count.count for count in response.statistics.tool_counts} == {
        "Bash": api_values.SHELL_COMMAND_COUNT,
        "Read": 4,
    }
    assert response.statistics.active_seconds == pytest.approx(api_values.ACTOR_ACTIVE_SECONDS)


def test_open_interval_is_added_when_route() -> None:
    """Verify an open interval is added when the route answers.

    `active_seconds` cannot be a stored number that grows on its own — the
        stored part is the closed intervals, and the one still open is measured
        against now.
    """
    response = mapper.actor(
        replace(
            api_values.ACTOR,
            statistics=actor_state.ActorStatistics(active_seconds=100.0, active_since_internal=1000.0),
        ),
        now=api_values.OPEN_INTERVAL_READ_TIME,
    )
    assert response.statistics.active_seconds == pytest.approx(api_values.OPEN_INTERVAL_TOTAL_SECONDS)


def test_writers_own_memory_never_reaches_client() -> None:
    """Verify the writers own memory never reaches a client.

    The internal fields exist so a restart resumes the fold. They are not
        facts about the session, and nothing outside the writers may see them.
    """
    response = mapper.session_data(
        session_state.SessionData(
            session=replace(
                api_values.FACTS,
                prompt_title_internal="the first thing asked",
                task_order_internal=(domain_ids.TaskId("t1"),),
            ),
            actors=(
                replace(
                    api_values.ACTOR,
                    pending_attention_internal=(domain_ids.AttentionId("att-3"),),
                    statistics=actor_state.ActorStatistics(file_paths_internal=("/work/a.py",)),
                ),
            ),
            cursor=1,
        ),
        live=False,
        repository_status=None,
    )

    encoded = response.model_dump_json()
    assert "internal" not in encoded
    assert "the first thing asked" not in encoded
    assert "/work/a.py" not in encoded
