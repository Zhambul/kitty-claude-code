# Copyright (c) 2026 Zhambyl Yermagambet
"""Build an automatic reply for a Claude Chrome permission request."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from pydantic import BaseModel, ConfigDict, Field

from harness.impl.claude_code.canonical.records import PermissionUpdate
from harness.impl.claude_code.hooks import constants

if TYPE_CHECKING:
    from harness.impl.claude_code.canonical.records import HookPayload


class ChromePermissionDecision(BaseModel):
    """Define the permission decision."""

    model_config = ConfigDict(frozen=True, populate_by_name=True)
    behavior: Literal["allow"] = "allow"
    updated_permissions: list[PermissionUpdate] | None = Field(
        default=None,
        alias="updatedPermissions",
    )


class ChromePermissionOutput(BaseModel):
    """Define the hook-specific permission output."""

    model_config = ConfigDict(frozen=True, populate_by_name=True)
    hook_event_name: str = Field(
        default="PermissionRequest",
        alias="hookEventName",
    )
    decision: ChromePermissionDecision


class ChromePermissionReply(BaseModel):
    """Define a complete permission reply."""

    model_config = ConfigDict(frozen=True, populate_by_name=True)
    hook_specific_output: ChromePermissionOutput = Field(alias="hookSpecificOutput")


def permission_reply(hook_payload: HookPayload) -> bytes:
    """Approve one Chrome request before Claude opens its dialog.

    Returns:
        The encoded reply, or empty bytes for another hook.

    """
    if hook_payload.hook_event_name != "PermissionRequest" or not (hook_payload.tool_name or "").startswith(
        constants.CHROME_TOOL_PREFIX,
    ):
        return b""
    session_updates = [
        suggestion
        for suggestion in hook_payload.permission_suggestions or ()
        if suggestion.behavior == "allow" and suggestion.destination == "session"
    ]
    reply = ChromePermissionReply(
        hookSpecificOutput=ChromePermissionOutput(
            decision=ChromePermissionDecision(
                updatedPermissions=session_updates or None,
            ),
        ),
    )
    return f"{reply.model_dump_json(by_alias=True, exclude_none=True)}\n".encode()
