# Copyright (c) 2026 Zhambyl Yermagambet
"""Verify terminal client architecture and behavior."""

from __future__ import annotations

import json
import os
import subprocess  # noqa: S404 -- Run local client entries against the test daemon.
import sys
from pathlib import Path
from typing import TYPE_CHECKING, TypedDict, Unpack

from tests import client_loading_runtime_dependencies as runtime_dependencies
from tests.client_test_servers import (
    _Capture,
    free_port,
)

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

CLIENT_TIMEOUT_SECONDS = 15


CLAUDE_HOOK = "claude_hook.py"


CLAUDE_STATUSLINE = "claude_statusline.py"


CODEX_HOOK = "codex_hook.py"


TERMINAL_KEYS = "terminal_keys.py"


PANE_WIDTH_PERCENT = 75


SESSION_ID_FIELD = "session_id"


TEST_SESSION_ID_TEXT = "session-one"


TEXT_ENCODING = "utf-8"


TEST_WINDOW_ID = "77"


RESIZE_AMOUNT = "9"


class ClientRunOptions(TypedDict, total=False):
    """Contain optional client process settings."""

    stdin: bytes
    port: int | None
    environment: Mapping[str, str] | None
    timeout: int


def run_client(
    name: str,
    arguments: Sequence[str] = (),
    **options: Unpack[ClientRunOptions],
) -> subprocess.CompletedProcess[bytes]:
    """Run a published client with the daemon port supplied in its environment.

    Returns:
        The completed process with captured output and error bytes.

    """
    process_environment = {
        variable_name: variable_content
        for variable_name, variable_content in os.environ.items()
        if not variable_name.startswith(("KITTY_", "CLAUDE_", "BAQYLAU_"))
    }
    port = options.get("port")
    process_environment["BAQYLAU_DASHBOARD_PORT"] = str(free_port() if port is None else port)
    process_environment.update(options.get("environment") or {})
    return subprocess.run(  # noqa: S603 -- Tests supply a local client name and separate arguments; no shell is used.
        [sys.executable, runtime_dependencies.clients.path(name), *arguments],
        input=options.get("stdin", b""),
        capture_output=True,
        env=process_environment,
        timeout=options.get("timeout", CLIENT_TIMEOUT_SECONDS),
        check=False,
    )


def test_claude_hook_ships_its_stdin_and_what_it(daemon: _Capture) -> None:
    """Verify the claude hook ships its stdin and what it observed.

    The check that runs the process. Every other hook test in the suite reads
        a file, which is exactly how a pane process that died on line 1 passed the
        whole suite.
    """
    daemon.reply = b'{"reply":"yes"}'
    payload = json.dumps(
        {SESSION_ID_FIELD: TEST_SESSION_ID_TEXT, "hook_event_name": "SessionStart"},
    ).encode(TEXT_ENCODING)

    completed = run_client(
        CLAUDE_HOOK,
        stdin=payload,
        port=daemon.port,
        environment={
            "KITTY_WINDOW_ID": TEST_WINDOW_ID,
            runtime_dependencies.claude_launcher.LAUNCH_MODEL_VARIABLE: "fable",
            runtime_dependencies.claude_launcher.LAUNCH_EFFORT_VARIABLE: "high",
        },
    )

    assert (completed.returncode, completed.stdout) == (0, b'{"reply":"yes"}')
    delivery = daemon.delivery("/hooks")
    assert (
        delivery.path,
        delivery.body,
        delivery.headers[runtime_dependencies.headers.TERMINAL_WINDOW_HEADER],
    ) == ("/api/harnesses/claude_code/hooks", payload, TEST_WINDOW_ID)
    # Its own pid, not the CLI's: the daemon walks the ancestry, while the CLI is
    # still blocked on this response and therefore provably alive.
    assert delivery.headers[runtime_dependencies.headers.CLIENT_PROCESS_HEADER].isdigit()
    assert (
        runtime_dependencies.headers.ACCOUNT_ID_HEADER not in delivery.headers
        and runtime_dependencies.headers.ACCOUNT_NAME_HEADER not in delivery.headers
    )
    assert (
        delivery.headers[runtime_dependencies.headers.LAUNCH_MODEL_HEADER] == "fable"
        and delivery.headers[runtime_dependencies.headers.LAUNCH_EFFORT_HEADER] == "high"
    )


def test_hook_of_daemons_own_probe_ships_nothing(daemon: _Capture) -> None:
    """Verify a hook of the daemons own probe ships nothing.

    The daemon spawns the harness to READ its plan windows, and that process
        fires hooks like any other. Shipping them would put a session in the store
        that nobody started — a reader manufacturing the thing it reads.
    """
    completed = run_client(
        CLAUDE_HOOK,
        stdin=b'{SESSION_ID_FIELD:"probe-session","hook_event_name":"SessionStart"}',
        port=daemon.port,
        environment={runtime_dependencies.claude_live_usage.PROBE_VARIABLE: "1"},
    )

    assert completed.returncode == 0
    assert completed.stdout == b""
    assert not daemon.deliveries


def test_the_codex_hook_ships_only_what_codex_has(daemon: _Capture) -> None:
    """Verify the codex hook ships only what codex has."""
    completed = run_client(
        CODEX_HOOK,
        stdin=b'{SESSION_ID_FIELD:"session-two"}',
        port=daemon.port,
        environment={"KITTY_WINDOW_ID": "12"},
    )

    assert completed.returncode == 0
    delivery = daemon.delivery("/hooks")
    assert delivery.path == "/api/harnesses/codex/hooks"
    assert delivery.headers[runtime_dependencies.headers.TERMINAL_WINDOW_HEADER] == "12"
    # No accounts, no launch selections: Codex has neither, so neither is claimed
    assert runtime_dependencies.headers.ACCOUNT_ID_HEADER not in delivery.headers
    assert runtime_dependencies.headers.LAUNCH_MODEL_HEADER not in delivery.headers


def test_statusline_only_runs_real_status_line(daemon: _Capture) -> None:
    """The shim keeps the configured display command and sends no usage data."""
    stdin = json.dumps(
        {
            SESSION_ID_FIELD: "session-usage",
            "rate_limits": {"five_hour": {"used_percentage": 25, "resets_at": 2_000_000_000}},
        },
    ).encode()

    completed = run_client(
        CLAUDE_STATUSLINE,
        arguments=[sys.executable, "-c", "import sys; sys.stdin.read(); print('HUD')"],
        stdin=stdin,
        port=daemon.port,
    )

    assert completed.returncode == 0
    assert completed.stdout == b"HUD\n"
    assert not daemon.deliveries


def test_keybinding_ships_only_its_env(daemon: _Capture) -> None:
    """Verify the keybinding ships only its environment."""
    for arguments in (["toggle"], ["grow", RESIZE_AMOUNT], ["setpct", "75"]):
        completed = run_client(
            TERMINAL_KEYS,
            arguments,
            port=daemon.port,
            environment={"KITTY_WINDOW_ID": TEST_WINDOW_ID},
        )
        assert completed.returncode == 0

    # one endpoint per gesture — the URL is the discriminator, so no body carries
    # a command word
    assert [delivery.path for delivery in daemon.deliveries] == [
        "/api/terminal/panes/toggle",
        "/api/terminal/panes/grow",
        "/api/terminal/panes/set-percent",
    ]
    toggle, grow, setpct = (json.loads(delivery.body) for delivery in daemon.deliveries)
    assert toggle == {"window_id": TEST_WINDOW_ID, "working_directory": str(Path.cwd())}
    assert grow["columns"] == int(RESIZE_AMOUNT)
    assert setpct["percent"] == PANE_WIDTH_PERCENT
