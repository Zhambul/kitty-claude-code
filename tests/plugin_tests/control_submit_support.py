# Copyright (c) 2026 Zhambyl Yermagambet
"""Cross-harness canonical translation tests from native fixture shapes."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from harness.models import controls as control_models
from tests.plugin_tests import vocabulary as fixture

QUEUE_CONFIRMATION_SUBMISSION = 2

if TYPE_CHECKING:
    from pathlib import Path

    from domain import (
        ids as domain_ids,
    )
    from harness.contract import (
        ComposerDriver,
    )
    from terminal.models import input as terminal_input
    from tests.plugin_tests.control_callback_values import TextSubmitCallback
    from tests.plugin_tests.control_state_values import DialogCall, SubmissionState


def accept_without_confirmation(
    submit_requirements: list[bool],
    _driver: ComposerDriver,
    _window: domain_ids.WindowId,
    _text: str,
    *,
    ensure_submit: bool = False,
) -> tuple[bool, bool]:
    """Record submission requirements without writing native confirmation.

    Returns:
        True for accepted input and False for clipboard-image clearing.

    """
    submit_requirements.append(ensure_submit)
    return True, False


def record_codex_title(
    calls: list[tuple[str, str]],
    _repository: object,
    source_reference: str,
    new_title: str,
) -> control_models.TitleWriteOutcome:
    """Record a native title write without changing a file.

    Returns:
        The successful rename outcome.

    """
    calls.append((source_reference, new_title))
    return control_models.TitleWriteOutcome.RENAMED


def submit_claude_queue(
    submission_state: SubmissionState,
    _driver: ComposerDriver,
    _window: domain_ids.WindowId,
    text: str,
    *,
    ensure_submit: bool = False,
) -> tuple[bool, bool]:
    """Record input and append queue confirmation on the second submission.

    Returns:
        True for accepted input and False for clipboard-image clearing.

    """
    source, delivered = submission_state
    delivered.append((text, ensure_submit))
    if len(delivered) == QUEUE_CONFIRMATION_SUBMISSION:
        with source.open(fixture.LETTER_A, encoding=fixture.TEXT_ENCODING) as transcript_file:
            transcript_file.write(
                json.dumps(
                    {
                        fixture.TYPE_FIELD: fixture.QUEUE_OPERATION_ID,
                        fixture.OPERATION_FIELD: fixture.ENQUEUE,
                        fixture.TIMESTAMP_FIELD: "2026-08-25T00:00:00.000Z",
                        "sessionId": fixture.SESSION_ONE_ID,
                        fixture.CONTENT_FIELD: text,
                    },
                )
                + "\n",
            )
    return True, False


def submit_codex_prompt(
    native_submit: TextSubmitCallback,
    source: Path,
    request: terminal_input.TextSubmitRequest,
) -> terminal_input.TextSubmitResponse:
    """Submit input and append a native Codex prompt record.

    Returns:
        The response from the supplied submission callback.

    """
    response = native_submit(request)
    with source.open(fixture.LETTER_A, encoding=fixture.TEXT_ENCODING) as rollout_file:
        rollout_file.write(
            json.dumps(
                {
                    fixture.TYPE_FIELD: fixture.RESPONSE_ITEM,
                    fixture.PAYLOAD_FIELD: {
                        fixture.TYPE_FIELD: fixture.MESSAGE_FIELD,
                        fixture.ID_FIELD: fixture.MESSAGE_ONE_ID,
                        fixture.ROLE_FIELD: fixture.USER,
                        fixture.CONTENT_FIELD: [
                            {
                                fixture.TYPE_FIELD: fixture.INPUT_TEXT_ID,
                                fixture.TEXT_FIELD: fixture.TEST,
                            },
                        ],
                        fixture.CHAT_METADATA_PASSTHROUGH_KIND: {
                            fixture.TURN_ID_FIELD: fixture.TURN_ONE_ID,
                        },
                    },
                },
            )
            + "\n",
        )
    return response


def submit_discussion(
    submission_state: tuple[Path, list[DialogCall]],
    _terminal: ComposerDriver,
    _window: domain_ids.WindowId,
    text: str,
    *,
    ensure_submit: bool = False,
) -> tuple[bool, bool]:
    """Record discussion input and write its native user message.

    Returns:
        True for accepted input and False for clipboard-image clearing.

    """
    source, calls = submission_state
    calls.append(("ensure-submit", ensure_submit))
    calls.append(("discussion", text))
    source.write_text(
        json.dumps(
            {
                fixture.TYPE_FIELD: fixture.USER,
                fixture.MESSAGE_FIELD: {fixture.CONTENT_FIELD: text},
            },
        )
        + "\n",
        encoding=fixture.TEXT_ENCODING,
    )
    return True, False


def submit_attachment(
    submission_state: SubmissionState,
    _terminal: ComposerDriver,
    _window: domain_ids.WindowId,
    text: str,
    *,
    ensure_submit: bool = False,
) -> tuple[bool, bool]:
    """Record attachment submission and write the fixed image message.

    Returns:
        True for accepted input and False for clipboard-image clearing.

    """
    source, delivered = submission_state
    delivered.append((text, ensure_submit))
    source.write_text(
        json.dumps(
            {
                fixture.TYPE_FIELD: fixture.USER,
                fixture.MESSAGE_FIELD: {
                    fixture.CONTENT_FIELD: [
                        {
                            fixture.TYPE_FIELD: fixture.TEXT_FIELD,
                            fixture.TEXT_FIELD: (
                                '[Image #1]Image attachment "marker.png":\nInspect the attached image.'
                            ),
                        },
                        {
                            fixture.TYPE_FIELD: fixture.IMAGE,
                            fixture.SOURCE: {
                                fixture.TYPE_FIELD: fixture.BASE64,
                                fixture.MEDIA_TYPE_FIELD: fixture.PNG_MEDIA_TYPE,
                                fixture.DATA_FIELD: "AA==",
                            },
                        },
                    ],
                },
            },
        )
        + "\n",
        encoding=fixture.TEXT_ENCODING,
    )
    return True, False


def submit_model(
    transcript_path: Path,
    _terminal: ComposerDriver,
    _window: domain_ids.WindowId,
    _text: str,
) -> tuple[bool, bool]:
    """Append a native model-selection command to the test transcript.

    Returns:
        True for accepted input and False for clipboard-image clearing.

    """
    with transcript_path.open(fixture.LETTER_A) as target:
        target.write(
            json.dumps(
                {
                    fixture.TYPE_FIELD: fixture.USER,
                    fixture.MESSAGE_FIELD: {
                        fixture.CONTENT_FIELD: "<command-name>/model</command-name><command-args>opus</command-args>",
                    },
                },
            )
            + "\n",
        )
    return True, False
