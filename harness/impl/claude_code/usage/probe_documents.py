# Copyright (c) 2026 Zhambyl Yermagambet
"""Declare the Claude Code control request and response lines."""

from typing import Literal

from pydantic import BaseModel, ConfigDict

from harness.impl.claude_code.ids import ClaudeCodeControlRequestId
from harness.impl.claude_code.usage.live_documents import GetUsageResponse

_OWNED = ConfigDict(extra="forbid", frozen=True)
_FOREIGN = ConfigDict(extra="ignore", frozen=True)
REQUEST_ID = ClaudeCodeControlRequestId("baqylau-usage")


class GetUsageRequest(BaseModel):
    """Request current usage from Claude Code."""

    model_config = _OWNED
    subtype: Literal["get_usage"] = "get_usage"


class ControlRequestLine(BaseModel):
    """Describe one control request line."""

    model_config = _OWNED
    type: Literal["control_request"] = "control_request"
    request_id: ClaudeCodeControlRequestId
    request: GetUsageRequest


class ControlResponseBody(BaseModel):
    """Describe the body of a successful control response."""

    model_config = _FOREIGN
    subtype: Literal["success"]
    request_id: ClaudeCodeControlRequestId
    response: GetUsageResponse | None = None


class ControlResponseLine(BaseModel):
    """Describe a complete successful control response."""

    model_config = _FOREIGN
    type: Literal["control_response"]
    response: ControlResponseBody


class ControlResponseIdentityBody(BaseModel):
    """Describe fields that identify a control response."""

    model_config = _FOREIGN
    request_id: ClaudeCodeControlRequestId | None = None


class ControlResponseIdentity(BaseModel):
    """Read only enough data to identify a control response."""

    model_config = _FOREIGN
    type: str | None = None
    response: ControlResponseIdentityBody | None = None


REQUEST = ControlRequestLine(
    request_id=REQUEST_ID,
    request=GetUsageRequest(),
)
