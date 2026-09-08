# Copyright (c) 2026 Zhambyl Yermagambet
"""Steps that check durable queued prompts."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

from pytest_bdd import parsers, then

if TYPE_CHECKING:
    from sdk import client as sdk_client
    from tests.e2e.testkit.references import Sessions
    from tests.e2e.testkit.session_contexts import SessionControlContext

QUEUE_POLL_SECONDS = 0.05


@then(
    parsers.parse(
        'session "{session_name}" has control "{control_name}" queued as prompt '
        "'{text}' after a fresh application read",
    ),
)
def session_has_durable_queued_prompt(
    session_control_context: SessionControlContext,
    session_name: str,
    control_name: str,
    text: str,
) -> None:
    """Wait for one durable queued prompt.

    Raises:
        AssertionError: If the prompt does not arrive before the deadline.

    """
    expected = [(session_control_context.controls.get(control_name).request_id, text)]
    deadline = time.monotonic() + session_control_context.wait_policy.pipeline
    while True:
        queue = session_control_context.prompts.client.preferences.session_state(
            session_control_context.prompts.sessions.get(session_name),
        ).composer.queue
        if queue is not None:
            messages = [(message.request_id, message.text) for message in queue.messages]
            if messages == expected:
                return
        if time.monotonic() >= deadline:
            message = f"queue does not contain {expected!r}"
            raise AssertionError(message)
        time.sleep(QUEUE_POLL_SECONDS)


@then(parsers.parse('session "{session_name}" has no queued prompts after a fresh application read'))
def session_has_no_durable_queued_prompts(
    client: sdk_client.BaqylauClient,
    sessions: Sessions,
    session_name: str,
) -> None:
    """Check that a session has no durable queued prompts."""
    queue = client.preferences.session_state(sessions.get(session_name)).composer.queue
    assert queue is None
