# Copyright (c) 2026 Zhambyl Yermagambet
"""Verify terminal client architecture and behavior."""

from __future__ import annotations

import contextlib
import subprocess  # noqa: S404 -- Run local client entries to check their usage errors.
import sys
import threading
from http import client as http_client
from types import MappingProxyType

from core import clients
from tests.test_client_programs import run_client

CLAUDE_HOOK = "claude_hook.py"


CLAUDE_STATUSLINE = "claude_statusline.py"


CLAUDE_OTEL = "claude_otel.py"


CODEX_HOOK = "codex_hook.py"


TERMINAL_PANE = "terminal_pane.py"


TERMINAL_KEYS = "terminal_keys.py"


TERMINAL_VIEW = "terminal_view.py"


TERMINAL_CONTENT = "terminal_content.py"


PUBLISHED = (CLAUDE_HOOK, CLAUDE_STATUSLINE, CODEX_HOOK, TERMINAL_KEYS, TERMINAL_VIEW, TERMINAL_CONTENT)


RECEIVER_POLL_SECONDS = 0.05


CLIENT_USAGE_TIMEOUT_SECONDS = 15
INVALID_ARGUMENT_EXIT_CODE = 2


USAGE = MappingProxyType({
    "claude_hook.py": ((), b"{SESSION_ID_FIELD:TEST_SESSION_ID_TEXT}"),
    "claude_statusline.py": ((), b"{SESSION_ID_FIELD:TEST_SESSION_ID_TEXT}"),
    "codex_hook.py": ((), b"{SESSION_ID_FIELD:TEST_SESSION_ID_TEXT}"),
    "terminal_keys.py": (("toggle",), b""),
    # Session, pane kind, target — the two click handlers reach the PANE now, not
    # the daemon, and with no pane running they must still say nothing.
    "terminal_view.py": (("baqylau-view://session-one/mirror/entry-9",), b""),
    "terminal_content.py": (("baqylau-content://session-one/mirror/sh:1:out",), b""),
})


def wait_for_receiver(port: int, attempts: int = 400) -> http_client.HTTPConnection:
    """Wait for the receiver to accept a connection.

    Returns:
        An open HTTP connection to the receiver.

    Raises:
        AssertionError: If all connection attempts fail.

    """
    for _ in range(attempts):
        connection = http_client.HTTPConnection("127.0.0.1", port, timeout=5)
        with contextlib.suppress(OSError):
            connection.connect()
            return connection
        connection.close()
        threading.Event().wait(RECEIVER_POLL_SECONDS)
    message = "the receiver never bound its port"
    raise AssertionError(message)


def test_client_is_silent_when_daemon_is_down() -> None:
    """R5, and the rule that lets every client be this small.

    A hook must never fail its harness, a keypress has nowhere to print and the
    status line must render regardless — so an unreachable daemon is not an
    error to report, it is a delivery that did not happen. The audit rows this
    gives up (`<harness> hook (deliver)`, `otel delivery (daemon unreachable)`)
    were bought with the sqlite layer in nine processes' failure paths.
    """
    for name in PUBLISHED:
        arguments, stdin = USAGE[name]
        completed = run_client(name, arguments, stdin=stdin)
        assert completed.returncode == 0, f"{name}: {completed.stderr!r}"
        assert completed.stdout == b"", name
        assert completed.stderr == b"", name


def test_client_says_how_to_use_it_and_refuses() -> None:
    """Verify a client says how to use it and refuses nothing else.

    Bad argv is the one failure a client may report: it comes from OUR config,
        not from the daemon, and it is what a human reads while writing that config.
    """
    for name in (TERMINAL_KEYS, TERMINAL_VIEW, TERMINAL_CONTENT):
        completed = run_client(name, ["nonsense"])
        assert completed.returncode == INVALID_ARGUMENT_EXIT_CODE, name
        assert b"usage:" in completed.stderr, name
    for name in (TERMINAL_PANE, CLAUDE_OTEL):
        completed = subprocess.run(  # noqa: S603 -- Only the two fixed local entry names are used, without a shell.
            [sys.executable, clients.path(name)],
            capture_output=True,
            timeout=CLIENT_USAGE_TIMEOUT_SECONDS,
            check=False,
        )
        assert completed.returncode == 1, name
        assert b"usage:" in completed.stderr, name
