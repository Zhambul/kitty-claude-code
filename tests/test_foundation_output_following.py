# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide test foundation output following."""

from __future__ import annotations

import pytest

from tests import foundation_dependencies, foundation_test_events, foundation_test_output

SESSION_ID_TEXT = "session-one"
PRIMARY_SESSION = foundation_dependencies.domain.domain_ids.SessionId(SESSION_ID_TEXT)
BACKGROUND_OPERATION_ID = "operation-bg"


@pytest.mark.usefixtures("database_path")
def test_bg_completion_fact_ends_following_early(
    tmp_path: foundation_dependencies.standard.Path) -> None:
    """Verify the background completion fact ends the following early.

    `operation.output_finished` is the background job's true end: the
        following stops there instead of stat-ing the file until the session dies.
    """
    following = foundation_test_output.started_background_following(tmp_path)
    assert len(following.storage.shell_output.find_for_session(PRIMARY_SESSION)) == 1
    following.reaction.react(
        foundation_dependencies.standard.replace(
            foundation_test_events.canonical_message(),
            payload=foundation_dependencies.domain.event_shell.ShellOutputFinished(
                foundation_dependencies.domain.domain_ids.ShellId(BACKGROUND_OPERATION_ID),
            ),
        ),
    )
    followings = following.storage.shell_output.find_for_session(PRIMARY_SESSION)
    assert len(followings) == 1
    raw_events = foundation_dependencies.engine.ShellOutputRawEventSource(
        followings[0], following.storage.shell_output,
    ).read(None)
    following.storage.recorder.record(raw_events)
    assert raw_events[-1].source_position == "finished"
    assert not following.storage.shell_output.find_for_session(PRIMARY_SESSION)
    assert following.output_path.exists()
