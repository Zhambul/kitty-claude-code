# Copyright (c) 2026 Zhambyl Yermagambet
"""Typed observations and gestures for a real session terminal."""

from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING

from sdk.client import BaqylauClient, wait_for
from tests.e2e.testkit import terminal_focus, terminal_geometry, terminal_topology

if TYPE_CHECKING:
    from terminal.contract import TerminalPlugin
    from terminal.models.values import WindowInfo
    from tests.e2e.testkit.policy import WaitPolicy
    from tests.e2e.testkit.references import SessionJourneyRef
    from tests.e2e.testkit.terminal_models import PaneGeometry, SessionPaneSet, TerminalFocus


def _assert_outcome(
    action: str,
    *,
    handled: bool,
    succeeded: bool,
    reason: str | None,
) -> None:
    if not handled or not succeeded:
        message = f"{action} failed: handled={handled}, succeeded={succeeded}, reason={reason!r}"
        raise AssertionError(message)


class _RealTerminalDriverState:
    """Store services that operate one real terminal."""

    def __init__(
        self,
        client: BaqylauClient,
        terminal: TerminalPlugin,
        wait_policy: WaitPolicy,
    ) -> None:
        """Initialize the object."""
        self._client = client
        self._terminal = terminal
        self._wait_policy = wait_policy


class _RealTerminalPanePresence(_RealTerminalDriverState):
    """Provide pane presence checks."""

    def wait_for_panes(self, journey: SessionJourneyRef) -> SessionPaneSet:
        """Wait for the session host, activity pane, and scoreboard.

        Returns:
            The complete session pane set.

        """
        session_id = journey.session.session_id
        return wait_for(
            lambda: f"session {session_id!r} to own one host, activity pane, and scoreboard",
            lambda: terminal_topology.pane_set(self._terminal, journey),
            timeout=self._wait_policy.feed,
        )

    def wait_for_no_auxiliary_panes(self, journey: SessionJourneyRef) -> None:
        """Process wait for no auxiliary panes."""
        session_id = journey.session.session_id
        wait_for(
            lambda: f"session {session_id!r} to keep only its host window",
            lambda: True if terminal_topology.host_only(self._terminal, journey) else None,
            timeout=self._wait_policy.feed,
        )

    def assert_host_window_exists(self, journey: SessionJourneyRef) -> None:
        """Process assert host window exists."""
        windows = self._terminal.metadata.windows()
        assert any(str(window.window_id) == journey.window_id for window in windows), (
            f"session host window {journey.window_id!r} is not on screen"
        )


class _RealTerminalPaneActions(_RealTerminalDriverState):
    """Provide terminal pane actions."""

    def toggle(self, journey: SessionJourneyRef) -> None:
        """Process toggle."""
        outcome = self._client.terminal.toggle_panes(
            window_id=journey.window_id,
            workspace=self._workspace(journey),
        )
        _assert_outcome(
            "toggle panes",
            handled=outcome.handled,
            succeeded=outcome.succeeded,
            reason=outcome.reason,
        )

    def grow(self, journey: SessionJourneyRef, columns: int) -> None:
        """Process grow."""
        outcome = self._client.terminal.grow_activity_pane(
            window_id=journey.window_id,
            workspace=self._workspace(journey),
            columns=columns,
        )
        _assert_outcome(
            "grow activity pane",
            handled=outcome.handled,
            succeeded=outcome.succeeded,
            reason=outcome.reason,
        )

    def shrink(self, journey: SessionJourneyRef, columns: int) -> None:
        """Process shrink."""
        outcome = self._client.terminal.shrink_activity_pane(
            window_id=journey.window_id,
            workspace=self._workspace(journey),
            columns=columns,
        )
        _assert_outcome(
            "shrink activity pane",
            handled=outcome.handled,
            succeeded=outcome.succeeded,
            reason=outcome.reason,
        )

    def set_percent(self, journey: SessionJourneyRef, percent: int) -> None:
        """Set percent."""
        outcome = self._client.terminal.set_activity_pane_width(
            window_id=journey.window_id,
            workspace=self._workspace(journey),
            percent=percent,
        )
        _assert_outcome(
            "set activity pane width",
            handled=outcome.handled,
            succeeded=outcome.succeeded,
            reason=outcome.reason,
        )

    def reset(self, journey: SessionJourneyRef) -> None:
        """Process reset."""
        outcome = self._client.terminal.reset_activity_pane(
            window_id=journey.window_id,
            workspace=self._workspace(journey),
        )
        _assert_outcome(
            "reset activity pane width",
            handled=outcome.handled,
            succeeded=outcome.succeeded,
            reason=outcome.reason,
        )

    def _workspace(self, journey: SessionJourneyRef) -> str:
        return self._client.sessions.snapshot(journey.session).session_data.session.working_directory


class _RealTerminalPaneGeometryWait(_RealTerminalPanePresence):
    """Provide terminal pane geometry waits."""

    def wait_for_width_change(
        self,
        journey: SessionJourneyRef,
        before: PaneGeometry,
        direction: str,
    ) -> PaneGeometry:
        """Wait for the activity pane width to change in the requested direction.

        Returns:
            The pane geometry after the width changes.

        """
        observed: list[PaneGeometry] = []
        return wait_for(
            partial(terminal_geometry.width_change_description, direction, before, observed),
            partial(terminal_geometry.width_change, self._terminal, journey, before, direction, observed),
            timeout=self._wait_policy.feed,
        )

    def wait_for_percent(self, journey: SessionJourneyRef, percent: int) -> PaneGeometry:
        """Wait for the activity pane to reach the requested width percentage.

        Returns:
            The matching pane geometry.

        """
        return wait_for(
            f"activity pane to have {percent} percent width",
            lambda: terminal_geometry.geometry_with_percent(self._terminal, journey, percent),
            timeout=self._wait_policy.feed,
        )


class _RealTerminalFocus(_RealTerminalDriverState):
    """Provide terminal focus checks."""

    def current_focus(self) -> TerminalFocus:
        """Read the current terminal focus.

        Returns:
            The focused window, tab, and Kitty application focus state.

        """
        return terminal_focus.current_focus(
            self._terminal.metadata.windows(),
            self._terminal.metadata.current_window_id(),
        )

    def assert_focus_preserved(self, before: TerminalFocus) -> None:
        """Check that a dashboard action preserved the terminal focus.

        Raises:
            AssertionError: If the previously focused window no longer exists.

        """
        windows = self._terminal.metadata.windows()
        found = terminal_topology.window_by_id(windows, before.window_id)
        if found is None:
            message = f"focused terminal window {before.window_id!r} is not on screen"
            raise AssertionError(message)
        focused = tuple(
            window_info for window_info in windows if window_info.tab_is_focused and window_info.is_active_in_tab
        )
        if before.kitty_focused:
            self._assert_kitty_focus(found, focused, before)
            return
        assert not focused, "the dashboard launch raised Kitty from the background"

    def _assert_kitty_focus(
        self,
        found: WindowInfo,
        focused: tuple[WindowInfo, ...],
        before: TerminalFocus,
    ) -> None:
        """Verify that the original Kitty window stays focused."""
        assert found.tab_is_focused
        assert found.tab_is_active
        assert found.is_active_in_tab
        assert str(found.tab_id) == before.tab_id
        assert {str(window_info.window_id) for window_info in focused} == {before.window_id}


class RealTerminalDriver(
    _RealTerminalPaneGeometryWait,
    _RealTerminalPaneActions,
    _RealTerminalFocus,
):
    """Provide the black-box terminal boundary for E2E journeys."""
