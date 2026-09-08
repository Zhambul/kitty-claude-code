# Copyright (c) 2026 Zhambyl Yermagambet
"""Test canonical sessiondata paint."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tests import (
    canonical_sessiondata_components as sessiondata_components,
    canonical_sessiondata_fixtures as session_fixtures,
    canonical_sessiondata_folding as folding,
    canonical_sessiondata_loop_support as loop_support,
    canonical_sessiondata_paint_support as paint_support,
    canonical_sessiondata_values as session_values,
)
from tests.canonical_sessiondata_components import domain as session_domain

if TYPE_CHECKING:
    from pathlib import Path


def test_tab_is_painted_from_status_that_was_just(tmp_path: Path) -> None:
    """Verify the tab is painted from the status that was just committed.

    The listener runs AFTER apply, which is the whole reason it is not a
        reaction: a reaction runs before the writers, where the status is still the
        previous one — so a session going idle would keep its old colour until some
        later, unrelated fact arrived.
    """
    tabs = paint_support.RecordingTabs()
    painter = sessiondata_components.terminal.tabs.TabColorPainter(
        tabs, paint_support.FixedSessions(session_values.LEAD),
    )
    loop, read_model = loop_support.loop_and_read_model(
        tmp_path,
        (
            *session_fixtures.alive(),
            session_domain.event_shell.ShellStarted(
                session_values.PRIMARY_SHELL_ID,
                session_values.SHELL_COMMAND_CONTENT,
                session_domain.outcomes.ExecutionMode.FOREGROUND,
                None,
            ),
        ),
        listener=painter,
    )

    loop.tick()

    # idle at birth, then executing — and nothing in between, because the
    # painter repaints only what changed.
    assert paint_support.paint_actions(tabs) == [session_values.PAINT_TOOL_NAME, session_values.PAINT_TOOL_NAME]
    assert session_fixtures.required_data(read_model).actors[0].status == session_values.EXECUTING_STATE


def test_finished_session_has_its_tab_colour(tmp_path: Path) -> None:
    """Verify a finished session has its tab colour cleared."""
    tabs = paint_support.RecordingTabs()
    loop, _read_model, _audit = loop_support.loop_over(
        tmp_path,
        (
            *session_fixtures.alive(),
            session_domain.event_session.SessionFinished(session_domain.outcomes.Outcome.SUCCEEDED, None),
        ),
        listener=sessiondata_components.terminal.tabs.TabColorPainter(
            tabs, paint_support.FixedSessions(session_values.LEAD),
        ),
    )

    loop.tick()

    assert tabs.painted[0][0] == session_values.PAINT_TOOL_NAME
    assert tabs.painted[1][0] == "clear"


def test_subagents_status_never_paints_sessions(tmp_path: Path) -> None:
    """Verify a subagents status never paints the sessions tab.

    A tab shows a session and a session shows its lead: a subagent turning
        red because it asked ITSELF something is not the session asking you.
    """
    tabs = paint_support.RecordingTabs()
    loop, _read_model, _audit = loop_support.loop_over(
        tmp_path,
        (
            *session_fixtures.alive(),
            folding.committed(
                session_domain.event_actor.ActorStarted(
                    session_values.EXPLORE_TASK_TEXT,
                    session_domain.messaging.ActorRole.CHILD,
                ),
                actor_id=session_values.CHILD,
                cursor=3,
            ).payload,
        ),
        listener=sessiondata_components.terminal.tabs.TabColorPainter(
            tabs, paint_support.FixedSessions(session_values.LEAD),
        ),
    )
    loop.tick()
    painted_before = list(tabs.painted)

    # …and a fact about the child changes nothing on the tab.
    loop.tick()
    assert tabs.painted == painted_before


def test_a_rebuild_repaints_nothing(tmp_path: Path) -> None:
    """Verify a rebuild repaints nothing.

    A replay of history through the writers must not touch the world: every
        session that ever finished would otherwise repaint its tab.
    """
    tabs = paint_support.RecordingTabs()
    loop, _read_model, _audit = loop_support.loop_over(
        tmp_path,
        session_fixtures.alive(),
        listener=sessiondata_components.terminal.tabs.TabColorPainter(
            tabs, paint_support.FixedSessions(session_values.LEAD),
        ),
    )
    loop.tick()
    painted_live = list(tabs.painted)
    assert painted_live

    loop.rebuild()

    assert tabs.painted == painted_live
