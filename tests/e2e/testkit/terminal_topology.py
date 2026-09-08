# Copyright (c) 2026 Zhambyl Yermagambet
"""Find the terminal windows for an E2E session."""

from __future__ import annotations

from typing import TYPE_CHECKING

from terminal.models.values import ACTIVITY_PANE_TAG, SCOREBOARD_PANE_TAG, SESSION_WINDOW_TAG
from tests.e2e.testkit.terminal_models import SessionPaneSet

if TYPE_CHECKING:
    from terminal.contract import TerminalPlugin
    from terminal.models.values import WindowInfo
    from tests.e2e.testkit.references import SessionJourneyRef

SESSION_WINDOW_COUNT = 3
SCOREBOARD_LINE_COUNT = 5


def pane_set(terminal: TerminalPlugin, journey: SessionJourneyRef) -> SessionPaneSet | None:
    """Return the complete pane set for one journey.

    Returns:
        The complete pane set for one journey.

    """
    windows = terminal.metadata.windows()
    host = window_by_id(windows, journey.window_id)
    if host is None:
        return None
    tab = tuple(window_info for window_info in windows if window_info.tab_id == host.tab_id)
    return _complete_pane_set(host, tab, journey)


def host_only(terminal: TerminalPlugin, journey: SessionJourneyRef) -> bool:
    """Return true when only the journey host remains.

    Returns:
        True when only the journey host remains.

    """
    windows = terminal.metadata.windows()
    host = window_by_id(windows, journey.window_id)
    if host is None:
        return False
    tab = tuple(window_info for window_info in windows if window_info.tab_id == host.tab_id)
    return tab == (host,) and _is_session_host(host, journey)


def window_by_id(windows: tuple[WindowInfo, ...], window_id: str) -> WindowInfo | None:
    """Return one visible terminal window by ID.

    Returns:
        One visible terminal window by ID.

    """
    return next((window_info for window_info in windows if str(window_info.window_id) == window_id), None)


def _complete_pane_set(
    host: WindowInfo,
    tab: tuple[WindowInfo, ...],
    journey: SessionJourneyRef,
) -> SessionPaneSet | None:
    activity = tuple(
        window_info for window_info in tab if window_info.tags.get(ACTIVITY_PANE_TAG) == journey.session.session_id
    )
    scoreboard = tuple(
        window_info for window_info in tab if window_info.tags.get(SCOREBOARD_PANE_TAG) == journey.session.session_id
    )
    if not _has_required_panes(tab, activity, scoreboard) or not _is_session_host(host, journey):
        return None
    activity_window = activity[0]
    scoreboard_window = scoreboard[0]
    if not _has_matching_auxiliary_panes(activity_window, scoreboard_window):
        return None
    return SessionPaneSet(host, activity_window, scoreboard_window)


def _has_required_panes(
    tab: tuple[WindowInfo, ...],
    activity: tuple[WindowInfo, ...],
    scoreboard: tuple[WindowInfo, ...],
) -> bool:
    has_three_windows = len(tab) == SESSION_WINDOW_COUNT
    has_one_activity = len(activity) == 1
    has_one_scoreboard = len(scoreboard) == 1
    return all((has_three_windows, has_one_activity, has_one_scoreboard))


def _is_session_host(host: WindowInfo, journey: SessionJourneyRef) -> bool:
    has_first_position = host.is_first_in_tab
    has_session_tag = host.tags.get(SESSION_WINDOW_TAG) == journey.session.session_id
    has_process = bool(host.processes)
    return all((has_first_position, has_session_tag, has_process))


def _has_matching_auxiliary_panes(activity: WindowInfo, scoreboard: WindowInfo) -> bool:
    activity_has_process = bool(activity.processes)
    scoreboard_has_process = bool(scoreboard.processes)
    has_scoreboard_height = scoreboard.lines == SCOREBOARD_LINE_COUNT
    has_equal_width = activity.columns == scoreboard.columns
    return all((activity_has_process, scoreboard_has_process, has_scoreboard_height, has_equal_width))
