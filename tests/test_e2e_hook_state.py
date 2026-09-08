# Copyright (c) 2026 Zhambyl Yermagambet
"""Copy trust only for the hooks included in the isolated profile."""

import json
import tomllib
from pathlib import Path

from tests.e2e.e2e_fixture_journeys import codex_hook_state_lines


def test_project_hook_trust_does_not_collide(tmp_path: Path) -> None:
    """Do not map project hook state onto the profile hook identity."""
    destination = tmp_path / "destination"
    source_hook = tmp_path / "hooks.json"
    global_key = json.dumps(f"{source_hook}:pre_tool_use:0:0")
    (tmp_path / "config.toml").write_text(
        f'[hooks.state.{global_key}]\ntrusted_hash="global"\n'
        '[hooks.state."/workspace/.codex/hooks.json:pre_tool_use:0:0"]\ntrusted_hash="project"\n',
    )
    copied = tomllib.loads("\n".join(codex_hook_state_lines(tmp_path, destination)))
    states = list(copied["hooks"]["state"].values())
    assert states == [{"trusted_hash": "global"}]
