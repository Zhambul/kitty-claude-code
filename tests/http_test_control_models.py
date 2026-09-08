# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide http test control models."""

from __future__ import annotations

from tests import (
    http_contract_dependencies as contract_dependencies,
    http_runtime_dependencies as runtime_dependencies,
    http_value_dependencies as standard_dependencies,
)

type JsonValue = bool | float | int | str | list[JsonValue] | dict[str, JsonValue] | None
type PaneCommandCall = tuple[str, runtime_dependencies.domain_ids.WindowId | None, str, int | None, int | None]


class NullInterruptRegistry:
    """Record an interrupt without changing live session state."""

    def mark(self, session_id: runtime_dependencies.domain_ids.SessionId) -> None:
        """Record the last marked session."""
        self.last_session_id = session_id


class NullControlEffects:
    """Record control effects without applying them to the application."""

    def work_before_close(
        self, session_id: runtime_dependencies.domain_ids.SessionId,
    ) -> tuple[contract_dependencies.open_session_work.SessionCloseWork, ...]:
        """Record a request for work that must finish before session closure.

        Returns:
            An empty work collection.

        """
        self._close_session_id = session_id
        return ()

    def message_queued(
        self, session: contract_dependencies.Session, send_text: runtime_dependencies.control_models.SendText,
    ) -> None:
        """Record the queued message."""
        self._queued_message = (session, send_text)

    def session_closed(
        self,
        session: contract_dependencies.Session,
        request: runtime_dependencies.control_models.CloseSession,
        observations: tuple[contract_dependencies.open_session_work.SessionCloseWork, ...],
    ) -> None:
        """Record the closed session and its work observations."""
        self._closed_session = (session, request, observations)

    def session_renamed(
        self,
        session: contract_dependencies.Session,
        rename_session: runtime_dependencies.control_models.RenameSession,
    ) -> None:
        """Record the session rename request."""
        self._renamed_session = (session, rename_session)

    def selection_changed(
        self,
        session: contract_dependencies.Session,
        selection: runtime_dependencies.control_models.SelectModel | runtime_dependencies.control_models.SelectEffort,
    ) -> None:
        """Record the model or effort selection."""
        self._changed_selection = (session, selection)

    def plan_decided(
        self,
        session: contract_dependencies.Session,
        decide_plan: runtime_dependencies.control_models.DecidePlan,
        pending_session_entry: runtime_dependencies.domain_entries.SessionEntry,
    ) -> None:
        """Record the plan decision and pending entry."""
        self._decided_plan = (session, decide_plan, pending_session_entry)


class PaneCommands:
    """Record pane commands and return a configured outcome."""

    def __init__(self) -> None:
        """Create an empty call list and a successful outcome."""
        self.calls: list[PaneCommandCall] = []
        self.outcome = contract_dependencies.PaneCommandOutcome(handled=True, succeeded=True)

    def toggle(
        self, window_id: runtime_dependencies.domain_ids.WindowId | None, working_directory: str,
    ) -> contract_dependencies.PaneCommandOutcome:
        """Record a pane toggle.

        Returns:
            The configured outcome.

        """
        self.calls.append(("toggle", window_id, working_directory, None, None))
        return self.outcome

    def grow(
        self,
        window_id: runtime_dependencies.domain_ids.WindowId | None,
        working_directory: str,
        columns: int | None = None,
    ) -> contract_dependencies.PaneCommandOutcome:
        """Record a pane growth request.

        Returns:
            The configured outcome.

        """
        self.calls.append(("grow", window_id, working_directory, columns, None))
        return self.outcome

    def shrink(
        self,
        window_id: runtime_dependencies.domain_ids.WindowId | None,
        working_directory: str,
        columns: int | None = None,
    ) -> contract_dependencies.PaneCommandOutcome:
        """Record a pane shrink request.

        Returns:
            The configured outcome.

        """
        self.calls.append(("shrink", window_id, working_directory, columns, None))
        return self.outcome

    def reset(
        self, window_id: runtime_dependencies.domain_ids.WindowId | None, working_directory: str,
    ) -> contract_dependencies.PaneCommandOutcome:
        """Record a pane width reset.

        Returns:
            The configured outcome.

        """
        self.calls.append(("reset", window_id, working_directory, None, None))
        return self.outcome

    def set_percent(
        self, window_id: runtime_dependencies.domain_ids.WindowId | None, working_directory: str, percent: int,
    ) -> contract_dependencies.PaneCommandOutcome:
        """Record a pane width percentage.

        Returns:
            The configured outcome.

        """
        self.calls.append(("setpct", window_id, working_directory, None, percent))
        return self.outcome


def json_object(json_content: JsonValue) -> dict[str, JsonValue]:
    """Return a JSON object and fail for a different JSON value.

    Returns:
        A JSON object and fail for a different JSON value.

    """
    assert isinstance(json_content, dict)
    return json_content


def execute_control_outcome(
    outcome: runtime_dependencies.control_models.ControlResult | Exception,
    _request: runtime_dependencies.control_models.SelectModel,
) -> runtime_dependencies.control_models.ControlResult:
    """Return the configured result, or raise a configured exception.

    Returns:
        The supplied control result when it is not an exception.

    """
    if isinstance(outcome, Exception):
        raise outcome
    return outcome


def control_invocation[Request: runtime_dependencies.control_models.ControlRequest](
    method: standard_dependencies.collections_abc.Callable[
        [Request], runtime_dependencies.control_models.ControlOutcome,
    ],
    request: Request,
) -> tuple[
    standard_dependencies.collections_abc.Callable[[], runtime_dependencies.control_models.ControlOutcome],
    runtime_dependencies.control_models.ControlRequest,
]:
    """Bind a control request to its method for an audit test.

    Returns:
        A callable with no arguments and its bound request.

    """
    return (lambda: method(request), request)
