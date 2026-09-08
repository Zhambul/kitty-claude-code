# Copyright (c) 2026 Zhambyl Yermagambet
"""Keep normal send confirmation local to its session."""

from pathlib import Path
from unittest.mock import Mock

import pytest

from harness.impl.codex.canonical import rollout, source_catalog
from harness.impl.codex.controls import controller_rollout


def test_normal_send_does_not_scan_history(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Take only the target session's initial position."""
    source = tmp_path / "session.jsonl"
    source.write_text("old input\n")
    catalog = source_catalog.RolloutCatalog(str(tmp_path))
    monkeypatch.setattr(catalog, "paths", Mock(side_effect=AssertionError("Unrelated history was scanned")))
    positions = controller_rollout.source_positions(catalog, str(source), discover=False)
    assert len(positions) == 1
    assert positions[0].position == source.stat().st_size


def test_confirmation_stops_at_prompt(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Do not translate later activity before confirming the prompt."""
    source = tmp_path / "session.jsonl"
    prompt = '{"type":"response_item","payload":{"type":"message","role":"user","content":"Go"}}'
    source.write_text(f"{prompt}\nnot a record\n")
    parse = Mock(wraps=rollout.parse_line)
    monkeypatch.setattr(rollout, "parse_line", parse)
    assert controller_rollout.confirmed_prompt_after(str(source), 0, "Go")
    parse.assert_called_once_with(prompt)
