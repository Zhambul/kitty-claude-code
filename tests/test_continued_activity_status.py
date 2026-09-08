# Copyright (c) 2026 Zhambyl Yermagambet
"""Keep fresh work active after an earlier turn ends."""

import pytest

from domain.content import TextContent
from domain.event_conversation import TurnStarted
from domain.event_shell import ShellFinished, ShellStarted
from domain.ids import ShellId
from domain.outcomes import ExecutionMode, Outcome
from tests import canonical_sessiondata_fixtures as fixtures


@pytest.mark.parametrize("explicit_turn", [False, True])
def test_new_work_after_a_stop_stays_active(*, explicit_turn: bool) -> None:
    """Do not show waiting-for-response between continued commands."""
    started = ShellStarted(ShellId("continued"), TextContent("echo continued"), ExecutionMode.FOREGROUND, None)
    finished = ShellFinished(ShellId("continued"), Outcome.SUCCEEDED, None, 0)
    continuation = (TurnStarted(None),) if explicit_turn else (started,)
    assert fixtures.status_after(fixtures.succeeded_turn(), *continuation, finished) == "working"
    assert (
        fixtures.status_after(fixtures.succeeded_turn(), *continuation, finished, fixtures.succeeded_turn())
        == "awaiting_response"
    )
