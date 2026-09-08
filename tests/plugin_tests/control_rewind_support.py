# Copyright (c) 2026 Zhambyl Yermagambet
"""Cross-harness canonical translation tests from native fixture shapes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from domain import (
    ids as domain_ids,
)
from harness import contract, runtime
from harness.impl.codex.plugin import build_plugin
from harness.models.session import (
    Session,
)
from tests.fake_terminal import FakeTerminal
from tests.plugin_tests import vocabulary as fixture
from tests.plugin_tests.control_codex_submit_support import insert_rewind_text, send_rewind_key

if TYPE_CHECKING:
    from pathlib import Path

    import pytest


@dataclass(frozen=True)
class RewindControlFixture:
    """Hold the session, terminal, and plugin for a rewind test."""

    session: Session
    terminal: FakeTerminal
    plugin: contract.HarnessPlugin


def rewind_sources(
    configuration_directory: Path,
    tmp_path: Path,
) -> tuple[Path, Path]:
    """Prepare the old rollout and the directory for a new rollout.

    Returns:
        The new rollout path and the existing empty old rollout path.

    """
    new_source = (
        configuration_directory
        / fixture.SESSIONS
        / fixture.YEAR_TEXT
        / fixture.MONTH_TEXT
        / "28"
        / "rollout-2026-08-28T20-00-00-new-session.jsonl"
    )
    new_source.parent.mkdir(parents=True)
    old_source = tmp_path / "old-rollout.jsonl"
    old_source.write_text("", encoding=fixture.TEXT_ENCODING)
    return new_source, old_source


def patch_rewind_terminal(
    monkeypatch: pytest.MonkeyPatch,
    terminal: FakeTerminal,
    new_source: Path,
) -> None:
    """Make terminal input update the screen and create the new rollout after Enter."""
    native_insert = terminal.insert_text
    native_key = terminal.send_key
    monkeypatch.setattr(
        terminal,
        "insert_text",
        lambda request: insert_rewind_text(native_insert, terminal, request),
    )
    monkeypatch.setattr(
        terminal,
        "send_key",
        lambda request: send_rewind_key(native_key, new_source, terminal, request),
    )


def rewind_control_fixture(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> RewindControlFixture:
    """Build an isolated Codex session with simulated rewind input.

    Returns:
        The old session, patched terminal, and configured Codex plugin.

    """
    configuration_directory = tmp_path / fixture.CODEX_HOME_ID
    new_source, old_source = rewind_sources(configuration_directory, tmp_path)
    terminal = FakeTerminal(screen_text=fixture.ASK_CODEX_TO_DO_ANYTHING_TEXT)
    patch_rewind_terminal(monkeypatch, terminal, new_source)
    session = Session(
        domain_ids.SessionId("old-session"),
        domain_ids.ActorId("old-session:lead"),
        str(old_source),
        str(tmp_path),
    )
    return RewindControlFixture(
        session,
        terminal,
        build_plugin(runtime.HarnessRuntimeConfig(fixture.CODEX_HARNESS, configuration_directory)),
    )
