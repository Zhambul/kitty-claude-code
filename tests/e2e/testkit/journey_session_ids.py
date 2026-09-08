# Copyright (c) 2026 Zhambyl Yermagambet
"""Read native session identifiers from unattended harness output."""

from __future__ import annotations

import json


def unattended_session_id(harness: str, output: str) -> str:
    """Return the native unattended session id.

    The harness reader raises AssertionError if no session identifier is present.

    Returns:
        The native session id.

    """
    return claude_session_id(output) if harness == "claude_code" else codex_session_id(output)


def claude_session_id(output: str) -> str:
    """Return the Claude session id.

    Returns:
        The Claude session id.

    Raises:
        AssertionError: If Claude does not report a session id.

    """
    try:
        return str(json.loads(output)["session_id"])
    except (json.JSONDecodeError, KeyError, TypeError) as error:
        message = f"Claude did not report a session id: {output!r}"
        raise AssertionError(message) from error


def codex_session_id(output: str) -> str:
    """Return the Codex thread id.

    Returns:
        The Codex thread id.

    Raises:
        AssertionError: If Codex does not report a thread id.

    """
    for line in output.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "thread.started" and event.get("thread_id"):
            return str(event["thread_id"])
    message = f"Codex did not report a thread id: {output!r}"
    raise AssertionError(message)
