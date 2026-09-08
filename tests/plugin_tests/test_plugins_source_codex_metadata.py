# Copyright (c) 2026 Zhambyl Yermagambet
"""Codex source metadata tests."""

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from domain import (
    ids as domain_ids,
)
from harness.impl.codex.canonical import rollout as codex_rollout
from harness.impl.codex.canonical.records import SessionMetaPayload, TurnContextRecord
from harness.impl.codex.canonical.sources import CodexRawEventSources
from harness.impl.codex.model import BaseInstructionsSourceType, CodexEffort, CodexModel
from harness.models.session import (
    Session,
)
from tests.plugin_tests import vocabulary as fixture
from tests.plugin_tests.source_codex_native_support import (
    rollout_path,
)


def test_codex_base_instruction_source_version() -> None:
    """Verify codex 0149 base instruction source is a closed vocabulary."""
    metadata = SessionMetaPayload.model_validate(
        {
            "base_instructions": {
                fixture.TEXT_FIELD: "You are Codex.",
                "provenance": {fixture.TYPE_FIELD: fixture.MODEL, fixture.MODEL: fixture.GPT_FIVE_SIX_LUNA},
            },
        },
    )

    assert metadata.base_instructions is not None
    assert metadata.base_instructions.source is not None
    assert metadata.base_instructions.source.type is BaseInstructionsSourceType.MODEL
    assert metadata.base_instructions.source.model is CodexModel.GPT_FIVE_SIX_LUNA


def test_codex_turn_context_model_and_effort() -> None:
    """Verify codex turn context model and effort are closed vocabularies."""
    record = codex_rollout.parse(
        {
            fixture.TYPE_FIELD: "turn_context",
            fixture.PAYLOAD_FIELD: {
                fixture.MODEL: fixture.GPT_FIVE_SIX_LUNA,
                fixture.EFFORT: "low",
                "root_turn_id": "root-turn",
            },
        },
    )

    assert isinstance(record, TurnContextRecord)
    assert record.model is CodexModel.GPT_FIVE_SIX_LUNA
    assert record.effort is CodexEffort.LOW


@pytest.mark.parametrize(
    ("field", "selection"),
    [(fixture.MODEL, "gpt-codex-next"), (fixture.EFFORT, "extreme")],
)
def test_codex_unknown_turn_context_selection(field: str, selection: str) -> None:
    """Verify codex unknown turn context selection is contract drift."""
    payload = {fixture.MODEL: fixture.GPT_FIVE_SIX_LUNA, fixture.EFFORT: "low"}
    payload[field] = selection

    with pytest.raises(ValidationError, match=field):
        codex_rollout.parse({fixture.TYPE_FIELD: "turn_context", fixture.PAYLOAD_FIELD: payload})


@pytest.mark.parametrize(
    ("field", "source_name"),
    [(fixture.TYPE_FIELD, "configuration"), (fixture.MODEL, "gpt-codex-next")],
)
def test_codex_unknown_base_instruction_source(field: str, source_name: str) -> None:
    """Verify codex unknown base instruction source value is contract drift."""
    source = {fixture.TYPE_FIELD: fixture.MODEL, fixture.MODEL: fixture.GPT_FIVE_SIX_LUNA}
    source[field] = source_name

    with pytest.raises(ValidationError, match=field):
        SessionMetaPayload.model_validate(
            {
                "base_instructions": {
                    fixture.TEXT_FIELD: "You are Codex.",
                    "provenance": source,
                },
            },
        )


@pytest.mark.usefixtures("codex_home", "monkeypatch")
def test_codex_source_factory_waits_for_native(
    tmp_path: Path) -> None:
    """Verify codex source factory waits for native child boundary."""
    child_path = rollout_path(
        tmp_path,
        fixture.FOURTEEN_TEXT,
        "rollout-2026-08-14T10-00-00-child-one.jsonl",
    )
    child_path.parent.mkdir(parents=True)
    child_path.write_text(
        json.dumps(
            {
                fixture.TYPE_FIELD: fixture.SESSION_META_ID,
                fixture.TIMESTAMP_FIELD: fixture.AUGUST_TIMESTAMP_TEXT,
                fixture.PAYLOAD_FIELD: {
                    fixture.THREAD_SOURCE: fixture.SUBAGENT,
                    fixture.PARENT_THREAD_ID_FIELD: fixture.PARENT_SESSION_ID,
                },
            },
        )
        + "\n",
    )
    session = Session(
        domain_ids.SessionId(fixture.PARENT_SESSION_ID),
        domain_ids.ActorId(fixture.PARENT_SESSION_LEAD_ID),
        str(tmp_path / fixture.NOT_A_CODEX_SESSION_JSONL_PATH),
        fixture.WORK_PATH,
    )

    assert CodexRawEventSources(tmp_path.as_posix()).for_session(session) == ()


@pytest.mark.usefixtures("codex_home", "monkeypatch")
def test_codex_source_factory_accepts_string(tmp_path: Path) -> None:
    """Verify codex source factory accepts string session source."""
    native_rollout_path = rollout_path(
        tmp_path,
        fixture.FOURTEEN_TEXT,
        "rollout-2026-08-14T10-00-00-regular-session.jsonl",
    )
    native_rollout_path.parent.mkdir(parents=True)
    native_rollout_path.write_text(
        json.dumps(
            {
                fixture.TYPE_FIELD: fixture.SESSION_META_ID,
                fixture.TIMESTAMP_FIELD: fixture.AUGUST_TIMESTAMP_TEXT,
                fixture.PAYLOAD_FIELD: {fixture.SOURCE: "vscode"},
            },
        )
        + "\n",
    )
    session = Session(
        domain_ids.SessionId(fixture.PARENT_SESSION_ID),
        domain_ids.ActorId(fixture.PARENT_SESSION_LEAD_ID),
        str(tmp_path / fixture.NOT_A_CODEX_SESSION_JSONL_PATH),
        fixture.WORK_PATH,
    )

    assert CodexRawEventSources(tmp_path.as_posix()).for_session(session) == ()
    assert codex_rollout.subagent_fork_epoch(str(native_rollout_path)) is None
