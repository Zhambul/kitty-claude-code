# Copyright (c) 2026 Zhambyl Yermagambet
"""Codex resume locator tests."""

from __future__ import annotations

from dataclasses import replace

from domain.ids import SessionId, WindowId
from harness.impl.codex.resume import CodexResumeLocator
from harness.models.session import LocatedSession
from terminal.models.values import WindowProcess
from tests.fake_terminal import window
from tests.plugin_tests import vocabulary as fixture


def test_codex_resume_locator_finds_direct() -> None:
    """Verify codex resume locator finds direct and login shell commands."""
    direct = replace(
        window(fixture.WINDOW_ONE_ID),
        processes=(
            WindowProcess(
                fixture.DIRECT_RESUME_PROCESS_ID,
                ("/opt/codex", "resume", "session-direct", "continue"),
            ),
        ),
    )
    login_shell = replace(
        window(fixture.WINDOW_TWO_ID),
        processes=(
            WindowProcess(
                fixture.SHELL_RESUME_PROCESS_ID,
                (
                    fixture.BIN_ZSH_PATH,
                    "-lic",
                    'codex "$@"',
                    fixture.CODEX_HARNESS,
                    "resume",
                    "session-shell",
                    "continue",
                ),
            ),
        ),
    )
    unrelated = replace(
        window("window-three"),
        processes=(
            WindowProcess(
                fixture.UNRELATED_PROCESS_ID,
                ("/opt/codex", "start", "work"),
            ),
        ),
    )

    assert CodexResumeLocator().locate((direct, login_shell, unrelated)) == (
        LocatedSession(SessionId("session-direct"), WindowId(fixture.WINDOW_ONE_ID)),
        LocatedSession(SessionId("session-shell"), WindowId(fixture.WINDOW_TWO_ID)),
    )
