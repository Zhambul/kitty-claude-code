# Copyright (c) 2026 Zhambyl Yermagambet
"""Common support for hook translation tests."""

from __future__ import annotations

import base64
import json
from typing import TYPE_CHECKING

from domain.ids import (
    SessionId,
)
from harness.impl.claude_code.hooks import gateway as claude_hooks
from tests.plugin_tests import support_hooks, vocabulary as fixture

if TYPE_CHECKING:
    from engine.interpret.loop import Interpreter
    from harness.models.hooks import HarnessHookResponse


PRIMARY_SESSION = SessionId(fixture.SESSION_ONE_ID)


def tick_interpreter(interpreter: Interpreter, count: int) -> None:
    """Run a fixed number of interpreter cycles."""
    for _ in range(count):
        interpreter.tick()


def encoded_json_document(document: object) -> bytes:
    """Encode one hook document as JSON bytes.

    Returns:
        The JSON document encoded as UTF-8 bytes.

    """
    return json.dumps(document).encode()


def receive_claude_hook(document: object) -> HarnessHookResponse:
    """Deliver one JSON hook document to the Claude gateway.

    Returns:
        The gateway reply and generated raw events.

    """
    payload = encoded_json_document(document)
    request = support_hooks.hook_request(payload)
    return claude_hooks.ClaudeHookGateway().receive_hook(request)


def decoded_output_content(payload: bytes) -> bytes:
    """Decode the stored base64 output content from one hook payload.

    Returns:
        The original output bytes.

    """
    document = json.loads(payload)
    return base64.b64decode(document["content_base64"])
