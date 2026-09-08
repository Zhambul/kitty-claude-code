# Copyright (c) 2026 Zhambyl Yermagambet
"""End-to-end coverage for automatic Claude-in-Chrome permissions."""

from __future__ import annotations

from contextlib import closing
from functools import partial
from typing import TYPE_CHECKING

import pytest

from sdk.client import BaqylauClient, SessionLaunchRequest
from tests.e2e.testkit import chrome_permission_checks, chrome_permission_process

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path

    from tests.e2e.testkit.process import ApplicationProcess

pytestmark = [pytest.mark.timeout(60)]
SESSION_ANNOUNCEMENT_TIMEOUT_SECONDS = 15


@pytest.fixture
def application_process(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[ApplicationProcess]:
    """Run the test-local Chrome permission application.

    Yields:
        The running application, stopped when the test ends.

    """
    process = chrome_permission_process.ChromeApplicationFactory(tmp_path).start(
        monkeypatch,
    )
    try:
        yield process
    finally:
        assert process.stop() == 0


@pytest.fixture(autouse=True)
def scenario_signoff() -> None:
    """Use the test-local process lifecycle instead of the shared scenario lifecycle."""


# Harness limit: claude_code only. Only Claude Code supports Chrome control.
def test_claude_chrome_permission_is_accepted(
    application_process: ApplicationProcess,
    tmp_path: Path,
) -> None:
    """Verify claude chrome permission is accepted automatically."""
    accepted = tmp_path / "chrome-accepted.txt"
    with closing(BaqylauClient(application_process.endpoint.url)) as client:
        launch = client.sessions.launch(
            SessionLaunchRequest(
                "claude_code",
                workspace=str(tmp_path),
                prompt="Open https://example.com in Chrome.",
                model=None,
                effort=None,
            ),
        )
        session = client.sessions.wait_for_session(
            launch,
            timeout=SESSION_ANNOUNCEMENT_TIMEOUT_SECONDS,
        )
        assert session.session_id == "00000000-0000-4000-8000-000000000738"
        chrome_permission_checks.wait(
            "Baqylau did not return the Chrome session permission",
            accepted.exists,
        )

        main_database = application_process.config.data_directory / "main.db"

        chrome_permission_checks.wait(
            "the Chrome permission request was not recorded",
            partial(
                chrome_permission_checks.permission_request_was_recorded,
                main_database,
                session.session_id,
            ),
        )

        chrome_permission_checks.wait(
            "the Chrome action did not become a Browser entry",
            partial(
                chrome_permission_checks.browser_action_was_recorded,
                main_database,
                session.session_id,
            ),
        )
