# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide browser usage."""

from __future__ import annotations

from tests.e2e.testkit import (
    browser_assertions,
    browser_capabilities,
    browser_client_dependencies as client_dependencies,
    browser_model_dependencies as model_dependencies,
    browser_runtime_dependencies as runtime_dependencies,
    browser_standard_dependencies as standard_dependencies,
    browser_values,
    references as browser_references,
)

browser_expectation = model_dependencies.expect
regular_expressions = standard_dependencies.re

HOUR_SECONDS = 3600


class BrowserTimingCapability(client_dependencies.Protocol):
    """Define shared browser timing and locator support."""

    def _milliseconds(self, seconds: float) -> float: ...

    def _record_console_error(self, console_message: client_dependencies.ConsoleMessage) -> None: ...

    def _record_request(self, request: client_dependencies.Request) -> None: ...

    def _omit_usage_row(self, harness: str, route: client_dependencies.Route) -> None: ...

    def _current_model_usage_window(
        self, harness: str, model: str,
    ) -> tuple[model_dependencies.UsageRowResponse, model_dependencies.UsageWindowResponse] | None: ...

    def _session_card(self, session: runtime_dependencies.SessionRef) -> client_dependencies.Locator: ...

    def _workspace_group(self) -> client_dependencies.Locator: ...


class BrowserFormCapability(client_dependencies.Protocol):
    """Define private browser session-form support."""

    def _launch_new_session(
        self, spec: browser_references.SessionSpec, prompt: str, workspace: str,
    ) -> runtime_dependencies.SessionRef: ...

    def _configure_fresh_session(
        self,
        dialog: client_dependencies.Locator,
        spec: browser_references.SessionSpec,
        workspace: str,
    ) -> None: ...

    def _open_new_session(self) -> client_dependencies.Locator: ...

    def _new_session_dialog(self) -> client_dependencies.Locator: ...

    def _select(self, dialog: client_dependencies.Locator, label: str, option: str) -> None: ...

    def _select_harness(self, dialog: client_dependencies.Locator, spec: browser_references.SessionSpec) -> None: ...

    def _select_account(self, dialog: client_dependencies.Locator, spec: browser_references.SessionSpec) -> None: ...


def duration_seconds(text: str) -> int:
    """Return the duration encoded in browser text.

    Returns:
        The duration encoded in browser text.

    Raises:
        AssertionError: If the text has no hours, minutes, or seconds.

    """
    hours = regular_expressions.search(r"(\d+)h", text)
    minutes = regular_expressions.search(r"(\d+)m", text)
    seconds = regular_expressions.search(r"(\d+)s", text)
    if hours is None and minutes is None and (seconds is None):
        msg = f"browser operation time is not readable: {text!r}"
        raise AssertionError(msg)
    return sum((
        browser_values.duration_component(hours, HOUR_SECONDS),
        browser_values.duration_component(minutes, 60),
        browser_values.duration_component(seconds, 1),
    ))


def file_diff_block(
    page: client_dependencies.Page,
    snapshot: runtime_dependencies.SessionSnapshot,
    reference: browser_references.FileOperationRef,
) -> client_dependencies.Locator:
    """Return the visible file diff block for one operation reference.

    Returns:
        The visible file diff block for one operation reference.

    """
    stream_blocks = page.locator(".stream .blk")
    operation_path = browser_assertions.file_operation_path(snapshot, reference)
    matching_path = page.locator(".bchips", has_text=operation_path)
    edit_marker = page.locator(".bchips > span:first-child", has_text="Edit")
    return stream_blocks.filter(has=matching_path).filter(has=edit_marker)


def assert_file_diff_coloring(block: client_dependencies.Locator, timeout_ms: float) -> None:
    """Verify the visible file diff colors and line markers."""
    if block.get_attribute("data-open") != "1":
        block.locator(".bhead").click()
    removed = block.locator(".tdiff .removed").first
    added = block.locator(".tdiff .added").first
    browser_expectation(removed).to_be_visible(timeout=timeout_ms)
    browser_expectation(added).to_be_visible(timeout=timeout_ms)
    browser_assertions.assert_mixed_background(removed, "--red", 24)
    browser_assertions.assert_mixed_background(added, "--green", 24)
    browser_assertions.assert_file_diff_markers(removed, added)


def plan_choice_label(
    outcome: model_dependencies.PlanChoicesResultResponse, action: browser_capabilities.BrowserPlanAction,
) -> str:
    """Return the dashboard label for a requested plan action.

    Returns:
        The dashboard label for a requested plan action.

    Raises:
        AssertionError: If the plan has no matching choice.

    """
    choices = [
        choice
        for choice in outcome.choices
        if choice.feedback == (action == browser_capabilities.BrowserPlanAction.feedback)
    ]
    if action == browser_capabilities.BrowserPlanAction.approve:
        choices = [choice for choice in choices if not choice.feedback]
    if not choices:
        msg = f"plan has no {action.value} choice"
        raise AssertionError(msg)
    return choices[0].label


def default_model_window(
    row: model_dependencies.UsageRowResponse, model: str,
) -> tuple[model_dependencies.UsageRowResponse, model_dependencies.UsageWindowResponse] | None:
    """Return one model window from one default harness row.

    Returns:
        The row and matching model window, or None if no window matches.

    Raises:
        AssertionError: If more than one window matches the model.

    """
    windows = row.windows
    matching_windows = [window for window in windows if browser_capabilities.is_requested_model_window(window, model)]
    matches = [(row, window) for window in matching_windows]
    if len(matches) > 1:
        msg = f"harness {row.harness!r} has {len(matches)} model usage windows for {model!r}"
        raise AssertionError(msg)
    return matches[0] if matches else None
