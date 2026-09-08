# Copyright (c) 2026 Zhambyl Yermagambet
"""Values for collaboration tests."""

from __future__ import annotations

from collections.abc import Callable

from domain import ids as domain_ids
from harness.models.raw_events import (
    TranslationResult,
)
from tests.plugin_tests import vocabulary as fixture
from tests.plugin_tests.support_values import JsonValue

type CodexRolloutTranslator = Callable[[JsonValue, str], TranslationResult]


type CodexPositionedRolloutTranslator = Callable[[JsonValue, str, str], TranslationResult]


type CollaborationArguments = dict[str, JsonValue]


PRIMARY_CHILD_ACTOR = domain_ids.ActorId(fixture.CHILD_ONE_ID)

COLLABORATION_CALLS: tuple[tuple[str, str, CollaborationArguments], ...] = (
    ("spawn", "spawn_agent", {"task_name": "weather", fixture.MESSAGE_FIELD: fixture.ENCRYPTED}),
    (
        "send",
        "send_message",
        {fixture.TARGET_FIELD: fixture.ROOT_WEATHER_PATH, fixture.MESSAGE_FIELD: fixture.ENCRYPTED},
    ),
    (
        "follow",
        "followup_task",
        {fixture.TARGET_FIELD: fixture.ROOT_WEATHER_PATH, fixture.MESSAGE_FIELD: fixture.ENCRYPTED},
    ),
    ("wait", "wait_agent", {"timeout_ms": 1000}),
    (fixture.INTERRUPT, "interrupt_agent", {fixture.TARGET_FIELD: fixture.ROOT_WEATHER_PATH}),
    ("list", "list_agents", {}),
)
