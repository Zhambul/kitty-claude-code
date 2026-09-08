# Copyright (c) 2026 Zhambyl Yermagambet
"""Parse attachment work step arguments."""

from __future__ import annotations

import re
from dataclasses import dataclass

LAUNCH_PATTERN = r'session "([^"\n]+)" and assign work "([^"\n]+)" to the (.+?) with attachment "([^"\n]+)"'
ASSIGNMENT_PATTERN = r'work "([^"\n]+)" in session "([^"\n]+)" to the (.+?) with attachment bundle "([^"\n]+)"'


@dataclass(frozen=True)
class AttachmentWorkNames:
    """Contain one parsed attachment work step."""

    session: str
    work: str
    worker_type: str
    attachment_source: str


def launch_names(text: str) -> AttachmentWorkNames:
    """Parse names from an attachment-work launch step.

    Returns:
        The parsed work names.

    Raises:
        AssertionError: If the step text has an invalid format.

    """
    matched_names = re.fullmatch(LAUNCH_PATTERN, text)
    if matched_names is None:
        message = f"invalid attachment work launch names: {text!r}"
        raise AssertionError(message)
    return AttachmentWorkNames(*matched_names.groups())


def assignment_names(text: str) -> AttachmentWorkNames:
    """Parse names from an attachment-work assignment step.

    Returns:
        The parsed work names.

    Raises:
        AssertionError: If the step text has an invalid format.

    """
    matched_names = re.fullmatch(ASSIGNMENT_PATTERN, text)
    if matched_names is None:
        message = f"invalid attachment work assignment names: {text!r}"
        raise AssertionError(message)
    return AttachmentWorkNames(
        matched_names.group(2),
        matched_names.group(1),
        matched_names.group(3),
        matched_names.group(4),
    )
