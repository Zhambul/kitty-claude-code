# Copyright (c) 2026 Zhambyl Yermagambet
"""Support for hook recording tests."""

import json
from dataclasses import dataclass
from pathlib import Path

import pytest

from domain.event_session import (
    SessionAccountChanged,
)
from domain.ids import (
    AccountId,
    SessionId,
    WindowId,
)
from harness.impl.claude_code.hooks import gateway as claude_hooks
from harness.impl.codex.hooks import gateway as codex_hooks
from tests.canonical_runtime import CanonicalRuntime
from tests.plugin_tests import support_hooks, support_runtime, vocabulary as fixture

SESSION_START_EVENT_COUNT = 2


@dataclass(frozen=True)
class HookRecordingFixture:
    """Hold the runtime, rollout path, and submitted hook payloads."""

    runtime: CanonicalRuntime
    rollout_path: Path
    claude_payload: bytes
    codex_payload: bytes


def hook_recording_fixture(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> HookRecordingFixture:
    """Deliver and interpret session-start hooks for both harnesses.

    Returns:
        The runtime and source data used by hook recording checks.

    """
    monkeypatch.setenv(fixture.BAQYLAU_DATA_DIR_ENV, tmp_path.as_posix())
    monkeypatch.setenv(fixture.CODEX_HOME_ENV, str(tmp_path / fixture.CODEX_HOME_ID))
    rollout_path = (
        tmp_path
        / fixture.CODEX_HOME_ID
        / fixture.SESSIONS
        / fixture.YEAR_TEXT
        / fixture.MONTH_TEXT
        / "15"
        / "rollout-2026-08-15T10-00-00-codex-session.jsonl"
    )
    rollout_path.parent.mkdir(parents=True)
    rollout_path.write_text(
        json.dumps(
            {
                fixture.TYPE_FIELD: fixture.SESSION_META_ID,
                fixture.PAYLOAD_FIELD: {
                    fixture.ID_FIELD: fixture.CODEX_SESSION_ID,
                    fixture.CWD_FIELD: fixture.WORK_PATH,
                    fixture.THREAD_SOURCE: fixture.USER,
                },
            },
        )
        + "\n",
    )
    claude_payload = (
        b'{ "session_id": "claude-session", "transcript_path": "/work/claude.jsonl", '
        b'"cwd": "/work", "session_title": "Saved resume title", '
        b'"hook_event_name": "SessionStart" }'
    )
    codex_payload = json.dumps(
        {
            fixture.SESSION_ID_FIELD: fixture.CODEX_SESSION_ID,
            fixture.TRANSCRIPT_PATH: str(rollout_path),
            fixture.CWD_FIELD: fixture.WORK_PATH,
            fixture.HOOK_EVENT_NAME_FIELD: fixture.SESSION_START_HOOK,
        },
    ).encode()
    support_hooks.deliver_hook(
        claude_hooks.ClaudeHookGateway(),
        claude_payload,
        terminal_window_id=WindowId(fixture.WINDOW_FIRST_ID),
        harness_process_id=fixture.FIXTURE_PROCESS_ID,
        account_id=AccountId("legacy-account"),
        account_display_name="Account Two",
    )
    support_hooks.deliver_hook(
        codex_hooks.CodexHookGateway(),
        codex_payload,
        terminal_window_id=WindowId("window-2"),
        harness_process_id=fixture.SECOND_FIXTURE_PROCESS_ID,
    )
    runtime, interpreter = support_runtime.interpreting_runtime(tmp_path / fixture.MAIN_DB_PATH)
    interpreter.tick()
    return HookRecordingFixture(runtime, rollout_path, claude_payload, codex_payload)


def assert_recorded_claude_session(recording_fixture: HookRecordingFixture) -> None:
    """Check the stored Claude source, terminal, and process identities."""
    claude_session = recording_fixture.runtime.sessions.find(SessionId(fixture.CLAUDE_SESSION_ID))
    assert claude_session is not None
    assert claude_session.source_reference == str(Path(fixture.WORK_CLAUDE_JSONL_PATH).resolve())
    assert claude_session.terminal_window_id == fixture.WINDOW_FIRST_ID
    assert claude_session.harness_process_id == fixture.FIXTURE_PROCESS_ID


def assert_recorded_codex_session(recording_fixture: HookRecordingFixture) -> None:
    """Check the stored Codex source and terminal identity."""
    codex_session = recording_fixture.runtime.sessions.find(SessionId(fixture.CODEX_SESSION_ID))
    assert codex_session is not None
    assert codex_session.source_reference == str(recording_fixture.rollout_path.resolve())
    assert codex_session.terminal_window_id == "window-2"


def assert_recorded_claude_audit(recording_fixture: HookRecordingFixture) -> None:
    """Check the Claude hook bytes and verify that no account change was inferred."""
    claude_audit = recording_fixture.runtime.raw_event_audits.audits_for_session(
        SessionId(fixture.CLAUDE_SESSION_ID),
    )[0]
    assert claude_audit.raw_event.payload == recording_fixture.claude_payload
    assert claude_audit.interpretation is not None
    assert len(claude_audit.interpretation.events) == SESSION_START_EVENT_COUNT
    account_changes = [
        recorded_event.event.payload
        for recorded_event in claude_audit.interpretation.events
        if isinstance(recorded_event.event.payload, SessionAccountChanged)
    ]
    assert not account_changes


def assert_recorded_codex_audit(recording_fixture: HookRecordingFixture) -> None:
    """Check the Codex hook bytes and translated event count."""
    codex_audit = recording_fixture.runtime.raw_event_audits.audits_for_session(
        SessionId(fixture.CODEX_SESSION_ID),
    )[0]
    assert codex_audit.raw_event.payload == recording_fixture.codex_payload
    assert codex_audit.interpretation is not None
    assert codex_audit.interpretation.decision == fixture.TRANSLATED
    assert len(codex_audit.interpretation.events) == SESSION_START_EVENT_COUNT
