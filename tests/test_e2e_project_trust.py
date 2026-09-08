# Copyright (c) 2026 Zhambyl Yermagambet
"""Check temporary Claude trust without using a real profile."""

import json
from pathlib import Path

import pytest

from tests.e2e.testkit.repository import ClaudeCodeProjectTrust

PROJECT = "/test-workspace"
PROJECTS_FIELD = "projects"
TEXT_ENCODING = "utf-8"


@pytest.mark.parametrize(PROJECTS_FIELD, [{}, {PROJECT: {"hasTrustDialogAccepted": False, "keep": "original"}}])
def test_project_trust_restores_previous_state(tmp_path: Path, projects: dict[str, object]) -> None:
    """Restore both absent and existing project records after temporary trust."""
    state_file = tmp_path / "state.json"
    original = {PROJECTS_FIELD: projects, "keep": "unrelated"}
    state_file.write_text(json.dumps(original), encoding=TEXT_ENCODING)
    trust = ClaudeCodeProjectTrust.grant(state_file, PROJECT)
    current = json.loads(state_file.read_text(encoding=TEXT_ENCODING))
    assert current[PROJECTS_FIELD][PROJECT]["hasTrustDialogAccepted"]
    trust.close()
    assert json.loads(state_file.read_text(encoding=TEXT_ENCODING)) == original


@pytest.mark.timeout(5)
def test_trust_recovers_after_invalid_state(tmp_path: Path) -> None:
    """Release the lock after invalid project data so a later grant can succeed."""
    state_file = tmp_path / "state.json"
    state_file.write_text('{"projects": []}', encoding=TEXT_ENCODING)
    with pytest.raises(TypeError, match="projects are not an object"):
        ClaudeCodeProjectTrust.grant(state_file, PROJECT)
    state_file.write_text('{"projects": {}}', encoding=TEXT_ENCODING)
    trust = ClaudeCodeProjectTrust.grant(state_file, PROJECT)
    trust.close()
    assert json.loads(state_file.read_text(encoding=TEXT_ENCODING)) == {PROJECTS_FIELD: {}}
