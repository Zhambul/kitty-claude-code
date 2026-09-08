# Copyright (c) 2026 Zhambyl Yermagambet
"""Test control effect message queue."""

from __future__ import annotations

import pytest

from domain import (
    content as domain_content,
    event_conversation,
)
from engine.interpret import translators as interpret_translators
from harness.models import controls as control_models
from tests import control_effect_recording as recording, control_effect_values as control_values


@pytest.mark.parametrize(
    ("text", "attachments", "expected"),
    [
        (control_values.NEXT_PROMPT, (), control_values.NEXT_PROMPT),
        (
            "",
            (control_models.AttachmentReference("/test-data/input.txt", "input.txt"),),
            "/test-data/input.txt",
        ),
    ],
)
def test_accepted_mid_turn_send_is_saved(
    text: str,
    attachments: tuple[control_models.AttachmentReference, ...],
    expected: str,
) -> None:
    """Verify an accepted mid turn send is saved by request identity."""
    control_fixture = recording.control_effect_fixture()
    request = control_models.SendText(
        control_values.TEST_SESSION_ID,
        control_values.TEST_REQUEST_ID,
        text=text,
        attachments=attachments,
    )

    control_fixture.recorder.message_queued(control_fixture.session, request)

    assert len(control_fixture.raw_events.events) == 1
    translated = interpret_translators.ControlTranslator().translate(control_fixture.raw_events.events[0])
    assert translated.canonical_events[0].payload == event_conversation.MessageQueued(
        control_values.TEST_REQUEST_ID,
        domain_content.TextContent(expected),
    )
