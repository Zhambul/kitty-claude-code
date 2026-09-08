# Copyright (c) 2026 Zhambyl Yermagambet
"""Cross-harness canonical translation tests from native fixture shapes."""

from __future__ import annotations

from pathlib import Path

from domain import (
    ids as domain_ids,
)
from tests.plugin_tests import vocabulary as fixture

type DialogCall = tuple[str, bool | str]


type SubmittedText = tuple[str, bool]


type SubmissionState = tuple[Path, list[SubmittedText]]

_BACKTRACK_STATE_TRANSITIONS = (
    ("composer", fixture.ESCAPE, "hint"),
    ("hint", fixture.ESCAPE, fixture.TRANSCRIPT_SOURCE),
    (fixture.TRANSCRIPT_SOURCE, fixture.ENTER, "restored"),
)


PRIMARY_SESSION = domain_ids.SessionId(fixture.SESSION_ONE_ID)


PRIMARY_ACTOR = domain_ids.ActorId(fixture.SESSION_ONE_LEAD_ID)


PRIMARY_REQUEST = domain_ids.RequestId(fixture.REQUEST_ONE_ID)


PRIMARY_WINDOW = domain_ids.WindowId(fixture.WINDOW_ONE_ID)
