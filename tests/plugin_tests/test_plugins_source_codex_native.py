# Copyright (c) 2026 Zhambyl Yermagambet
"""Native Codex rollout source tests."""

import json
from pathlib import Path

import pytest

from domain import (
    event_actor,
    event_session,
    ids as domain_ids,
)
from harness.impl.codex.canonical.sources import CodexRawEventSources
from harness.impl.codex.canonical.translator import CodexCanonicalTranslator
from harness.models.session import (
    Session,
)
from tests.plugin_tests import (
    source_catalog_support,
    source_codex_assert_support,
    source_codex_native_support,
    source_codex_reuse_support,
    source_common_support,
    vocabulary as fixture,
)
from tests.plugin_tests.support_events import payloads

pytestmark = pytest.mark.usefixtures("codex_home", "monkeypatch")
CHANGED_DIRECTORY_SCANS = 2
REPEATED_SOURCE_LOOKUPS = 2
FINAL_SOURCE_LOOKUPS = 3


def test_codex_source_factory_includes_native(
    tmp_path: Path,
) -> None:
    """Verify codex source factory includes native subagent rollouts."""
    child_source = source_codex_native_support.native_codex_child_source(tmp_path)
    raw_events = child_source.read(None)
    translator = CodexCanonicalTranslator()

    source_codex_assert_support.assert_child_source_context(child_source, raw_events, translator)
    source_codex_assert_support.assert_child_replay_records(raw_events, translator)
    source_codex_assert_support.assert_child_records(raw_events, translator)


def test_codex_rollout_catalog_rescans_only(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify codex rollout catalog rescans only a changed date directory."""
    day_directory = source_codex_native_support.rollout_directory(tmp_path, "24")
    day_directory.mkdir(parents=True)
    first = day_directory / "rollout-2026-08-24T10-00-00-first.jsonl"
    first.write_text(fixture.EMPTY_JSON_LINE)
    scanned: list[str] = []
    catalog = source_catalog_support.tracked_rollout_catalog(tmp_path, monkeypatch, scanned)

    assert catalog.paths() == (str(first),)
    assert catalog.paths() == (str(first),)
    assert scanned.count(str(day_directory)) == 1

    second = day_directory / "rollout-2026-08-24T10-00-01-second.jsonl"
    second.write_text(fixture.EMPTY_JSON_LINE)

    assert catalog.paths() == (str(first), str(second))
    assert scanned.count(str(day_directory)) == CHANGED_DIRECTORY_SCANS


def test_codex_source_factory_reuses_sources(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Reuse readers and check the catalog on each input notice."""
    source_fixture = source_codex_reuse_support.codex_source_reuse_fixture(tmp_path, monkeypatch)
    first = source_fixture.factory.for_session(source_fixture.session)
    second = source_fixture.factory.for_session(source_fixture.session)
    assert first == second
    assert source_codex_native_support.same_objects(first, second)
    assert len(source_fixture.catalog_invocations) == REPEATED_SOURCE_LOOKUPS

    source_fixture.factory.for_session(source_fixture.session)
    assert len(source_fixture.catalog_invocations) == FINAL_SOURCE_LOOKUPS


def test_codex_source_factory_rotates_native(tmp_path: Path) -> None:
    """Verify codex source factory rotates native subagent rollouts."""
    sessions_directory = source_codex_native_support.native_session_directory(tmp_path)
    sessions_directory.mkdir(parents=True)
    for child_name in (fixture.CHILD_ONE_ID, "child-two"):
        child_path = sessions_directory / f"rollout-2026-08-14T10-00-00-{child_name}.jsonl"
        child_path.write_text(
            json.dumps(
                {
                    fixture.TYPE_FIELD: fixture.SESSION_META_ID,
                    fixture.TIMESTAMP_FIELD: fixture.AUGUST_TIMESTAMP_TEXT,
                    fixture.PAYLOAD_FIELD: {
                        fixture.CWD_FIELD: fixture.WORK_PATH,
                        fixture.THREAD_SOURCE: fixture.SUBAGENT,
                        fixture.PARENT_THREAD_ID_FIELD: fixture.PARENT_SESSION_ID,
                        fixture.TIMESTAMP_FIELD: fixture.AUGUST_TIMESTAMP_TEXT,
                    },
                },
            )
            + "\n"
            + json.dumps(
                {
                    fixture.TYPE_FIELD: fixture.EVENT_MSG_ID,
                    fixture.PAYLOAD_FIELD: {
                        fixture.TYPE_FIELD: "user_message",
                        fixture.MESSAGE_FIELD: "parent replay",
                    },
                },
            )
            + "\n"
            + json.dumps(
                {
                    fixture.TYPE_FIELD: fixture.EVENT_MSG_ID,
                    fixture.PAYLOAD_FIELD: {
                        fixture.TYPE_FIELD: fixture.TASK_STARTED_ID,
                        fixture.STARTED_AT: 1786701600,
                    },
                },
            )
            + "\n"
            + json.dumps(
                {
                    fixture.TYPE_FIELD: fixture.EVENT_MSG_ID,
                    fixture.PAYLOAD_FIELD: {
                        fixture.TYPE_FIELD: "agent_message",
                        fixture.MESSAGE_FIELD: "child work",
                    },
                },
            )
            + "\n",
        )
    factory = CodexRawEventSources(tmp_path.as_posix())
    actors = source_codex_reuse_support.rotated_source_actors(
        factory,
        Session(
            domain_ids.SessionId(fixture.PARENT_SESSION_ID),
            domain_ids.ActorId(fixture.PARENT_SESSION_LEAD_ID),
            str(tmp_path / fixture.NOT_A_CODEX_SESSION_JSONL_PATH),
            fixture.WORK_PATH,
        ),
    )

    assert actors == [
        domain_ids.ActorId(fixture.CHILD_ONE_ID),
        domain_ids.ActorId("child-two"),
    ]


def test_codex_session_start_announces_only_lead(
    tmp_path: Path) -> None:
    """Verify codex session start announces only a lead rollout."""
    lead_path = source_codex_native_support.rollout_path(tmp_path, "15", "rollout-2026-08-15T10-00-00-lead-one.jsonl")
    lead_path.parent.mkdir(parents=True)
    lead_path.write_text(
        json.dumps(
            {
                fixture.TYPE_FIELD: fixture.SESSION_META_ID,
                fixture.PAYLOAD_FIELD: {
                    fixture.ID_FIELD: fixture.LEAD_ONE_ID,
                    fixture.CWD_FIELD: fixture.WORK_PATH,
                    fixture.THREAD_SOURCE: fixture.USER,
                    "base_instructions": {
                        fixture.TEXT_FIELD: "You are Codex.",
                        "provenance": {
                            fixture.TYPE_FIELD: fixture.MODEL,
                            fixture.MODEL: fixture.GPT_FIVE_SIX_LUNA,
                        },
                    },
                },
            },
        )
        + "\n",
    )
    child_path = lead_path.with_name("rollout-2026-08-15T10-00-01-child-one.jsonl")
    child_path.write_text(
        json.dumps(
            {
                fixture.TYPE_FIELD: fixture.SESSION_META_ID,
                fixture.PAYLOAD_FIELD: {
                    fixture.THREAD_SOURCE: fixture.SUBAGENT,
                    fixture.PARENT_THREAD_ID_FIELD: fixture.LEAD_ONE_ID,
                },
            },
        )
        + "\n",
    )

    translator = CodexCanonicalTranslator()
    lead = translator.translate(source_common_support.session_start_hook_event(fixture.LEAD_ONE_ID, lead_path))
    child = translator.translate(source_common_support.session_start_hook_event(fixture.CHILD_ONE_ID, child_path))

    assert len(payloads(lead, event_session.SessionStarted)) == 1
    assert payloads(
        lead,
        event_session.SessionStarted,
    )[0].payload.source_reference == str(lead_path.resolve())
    assert child.decision == fixture.IGNORED_NONSEMANTIC
    assert child.canonical_events == ()


def test_later_codex_lead_hook_recovers_missed(
    tmp_path: Path) -> None:
    """Verify a later codex lead hook recovers a missed run start."""
    native_rollout_path = source_codex_native_support.rollout_path(
        tmp_path, "25", "rollout-2026-08-25T10-00-00-session-one.jsonl",
    )
    native_rollout_path.parent.mkdir(parents=True)
    native_rollout_path.write_text(
        json.dumps(
            {
                fixture.TYPE_FIELD: fixture.SESSION_META_ID,
                fixture.PAYLOAD_FIELD: {
                    fixture.ID_FIELD: fixture.SESSION_ONE_ID,
                    fixture.CWD_FIELD: fixture.WORK_PATH,
                    fixture.THREAD_SOURCE: fixture.USER,
                },
            },
        )
        + "\n",
    )

    translator = CodexCanonicalTranslator()
    native_start = translator.translate(
        source_common_support.codex_hook_event(native_rollout_path, fixture.SESSION_START_HOOK, "native-start"),
    )
    later_hook = translator.translate(
        source_common_support.codex_hook_event(native_rollout_path, fixture.PRE_TOOL_USE_HOOK, "later-tool"),
    )

    assert [type(event.payload) for event in later_hook.canonical_events] == [
        event_session.SessionStarted,
        event_actor.ActorStarted,
    ]
    assert [event.event_id for event in later_hook.canonical_events] == [
        event.event_id for event in native_start.canonical_events
    ]
