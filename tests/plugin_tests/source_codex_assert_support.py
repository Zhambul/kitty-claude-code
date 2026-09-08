# Copyright (c) 2026 Zhambyl Yermagambet
"""Assertions for native Codex source tests."""

from __future__ import annotations

from typing import TYPE_CHECKING

from domain import (
    event_actor,
    event_conversation,
    ids as domain_ids,
)
from tests.plugin_tests import vocabulary as fixture
from tests.plugin_tests.support_events import payloads
from tests.plugin_tests.support_values import text_of

if TYPE_CHECKING:
    from harness.impl.codex.canonical.source_readers import (
        CodexRolloutRawEventSource,
    )
    from harness.impl.codex.canonical.translator import CodexCanonicalTranslator
    from harness.models import raw_events as raw_event_models


def assert_child_source_context(
    child_source: CodexRolloutRawEventSource,
    raw_events: tuple[raw_event_models.RawEvent, ...],
    translator: CodexCanonicalTranslator,
) -> None:
    """Verify the child source actor context and start record."""
    assert child_source.context.actor_id == domain_ids.ActorId(fixture.CHILD_ONE_ID)
    assert child_source.context.parent_actor_id == domain_ids.ActorId(fixture.PARENT_SESSION_LEAD_ID)
    translation = translator.translate(raw_events[0])
    started = payloads(translation, event_actor.ActorStarted)[0].payload
    assert started.role == "sidecar"


def assert_child_replay_records(
    raw_events: tuple[raw_event_models.RawEvent, ...],
    translator: CodexCanonicalTranslator,
) -> None:
    """Verify the parent records that replay into the child source."""
    assert raw_events[1].source_type == "sidecar_replay"
    replay = translator.translate(raw_events[1])
    assert replay.canonical_events == ()
    assert replay.decision == fixture.IGNORED_NONSEMANTIC
    # The parent's replayed task_started (started_at BEFORE the fork) is prefix;
    # the child's OWN bootstrap task_started (started_at >= the fork) is the
    # first child-own record — classified as replay it eats the child's
    # turn/assignment start (session 01a00a31-3a90 painted no started card).
    assert raw_events[2].source_type == "sidecar_replay"


def assert_child_records(
    raw_events: tuple[raw_event_models.RawEvent, ...],
    translator: CodexCanonicalTranslator,
) -> None:
    """Verify the child-owned rollout records."""
    assert raw_events[3].source_type == "sidecar_rollout"
    assert payloads(translator.translate(raw_events[3]), event_conversation.TurnStarted)
    assert raw_events[4].source_type == "sidecar_rollout"
    message = payloads(translator.translate(raw_events[4]), event_conversation.MessageCreated)[0]
    assert text_of(message.payload.content) == "child work"
