# Copyright (c) 2026 Zhambyl Yermagambet
"""Build native hook documents for control effect tests."""

import json

from tests import control_effect_values as control_values


def hook_payload(event_name: str, event_id: str) -> bytes:
    """Build one native session hook document.

    Returns:
        One native session hook document.

    """
    return json.dumps(
        {
            "session_id": control_values.TEST_SESSION_ID_TEXT,
            "transcript_path": "/transcripts/session-one.jsonl",
            "cwd": control_values.TEST_WORKING_DIRECTORY,
            "hook_event_name": event_name,
            "hook_event_id": event_id,
        },
    ).encode()
