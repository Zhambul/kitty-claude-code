#!/usr/bin/env python3
# Copyright (c) 2026 Zhambyl Yermagambet
"""A Claude terminal fixture that asks for a Chrome site permission."""

from __future__ import annotations

import json
import os
from http import HTTPStatus
from pathlib import Path
from threading import Event
from urllib import request as urllib_request

SESSION_ID = "00000000-0000-4000-8000-000000000738"
CALL_ID = "chrome-navigation-738"
type JsonObject = dict[str, object]


def _hook(payload: JsonObject) -> JsonObject:
    hook_request = urllib_request.Request(
        f"http://127.0.0.1:{os.environ['BAQYLAU_DASHBOARD_PORT']}/api/harnesses/claude_code/hooks",
        data=f"{json.dumps(payload)}\n".encode(),
        headers={
            "Content-Type": "application/json",
            "X-Baqylau-Terminal-Window": os.environ["BAQYLAU_PTY_WINDOW_ID"],
            "X-Baqylau-Client-Process": str(os.getpid()),
        },
        method="POST",
    )
    with urllib_request.urlopen(hook_request, timeout=10) as response:  # noqa: S310 -- Send the fixture hook to the fixed loopback HTTP host.
        if response.status != HTTPStatus.OK:
            message = f"hook delivery returned {response.status}"
            raise RuntimeError(message)
        body = response.read()
    return json.loads(body) if body else {}


def _payload(transcript: str, hook_name: str, **hook_fields: object) -> JsonObject:
    return {
        "session_id": SESSION_ID,
        "transcript_path": transcript,
        "cwd": str(Path.cwd()),
        "hook_event_name": hook_name,
        **hook_fields,
    }


def _permission_failure(reply: JsonObject, session_update: JsonObject) -> Exception | None:
    """Return a failure for an invalid permission reply.

    Returns:
        A failure for an invalid permission reply.

    """
    output = reply.get("hookSpecificOutput")
    if not isinstance(output, dict):
        return TypeError("Chrome permission output is absent")
    decision = output.get("decision")
    if not isinstance(decision, dict):
        return TypeError("Chrome permission decision is absent")
    behavior = decision.get("behavior")
    if behavior != "allow":
        return RuntimeError("Chrome permission was not allowed")
    updates = decision.get("updatedPermissions")
    if updates != [session_update]:
        return RuntimeError("Chrome session permission was not returned")
    return None


def main() -> None:
    """Process main."""
    transcript = str(Path.cwd() / "fake-claude-chrome.jsonl")
    Path(transcript).write_text("", encoding="utf-8")
    _hook(_payload(transcript, "SessionStart", source="startup"))
    _hook(
        _payload(
            transcript,
            "PreToolUse",
            tool_use_id=CALL_ID,
            tool_name="mcp__claude-in-chrome__navigate",
            tool_input={"url": "https://example.com"},
        ),
    )
    session_update: JsonObject = {
        "type": "addRules",
        "rules": [
            {
                "toolName": "ClaudeInChromeDomain",
                "ruleContent": "example.com",
            },
        ],
        "behavior": "allow",
        "destination": "session",
    }
    reply = _hook(
        _payload(
            transcript,
            "PermissionRequest",
            tool_name="mcp__claude-in-chrome__navigate",
            tool_input={"url": "https://example.com"},
            permission_suggestions=[session_update],
        ),
    )
    permission_failure = _permission_failure(reply, session_update)
    if permission_failure is not None:
        raise permission_failure
    Path(os.environ["BAQYLAU_E2E_CHROME_ACCEPTED"]).write_text(
        json.dumps(reply),
        encoding="utf-8",
    )
    _hook(
        _payload(
            transcript,
            "PostToolUse",
            tool_use_id=CALL_ID,
            tool_name="mcp__claude-in-chrome__navigate",
            tool_input={"url": "https://example.com"},
            tool_response={"content": "Example Domain loaded"},
        ),
    )
    Event().wait()


if __name__ == "__main__":
    main()
