# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide browser session forms."""

from __future__ import annotations

from tests.e2e.testkit import (
    browser_assertions,
    browser_capabilities,
    browser_client_dependencies as client_dependencies,
    browser_model_dependencies as model_dependencies,
    browser_runtime_dependencies as runtime_dependencies,
    browser_standard_dependencies as standard_dependencies,
    browser_usage,
    references as browser_references,
)

browser_expectation = model_dependencies.expect

NO_KNOWN_SESSIONS: frozenset[str] = frozenset()


def _weekly_usage_window(
    row: model_dependencies.UsageRowResponse,
) -> model_dependencies.UsageWindowResponse | None:
    """Return the weekly account usage window for one row.

    Returns:
        The weekly account usage window for one row.

    """
    return next((window for window in row.windows if browser_capabilities.is_weekly_account_window(window)), None)


class BrowserPageCapability(client_dependencies.Protocol):
    """Define private browser page and attention support."""

    def _select_model_and_effort(
        self,
        dialog: client_dependencies.Locator,
        spec: browser_references.SessionSpec,
        workspace: str,
    ) -> None: ...

    def _wait_for_visible_session(
        self, known: frozenset[str] = NO_KNOWN_SESSIONS,
    ) -> runtime_dependencies.SessionRef: ...

    def _wait_for_session_url(self, session: runtime_dependencies.SessionRef) -> None: ...

    def _resume_option(self, source: runtime_dependencies.SessionRef) -> client_dependencies.Locator: ...

    def _wait_for_question_resolution(self, reference: browser_references.QuestionRef) -> None: ...

    def _submit_plan_action(
        self,
        reference: browser_references.PlanRef,
        action: browser_capabilities.BrowserPlanAction,
        feedback: str | None,
        card: client_dependencies.Locator,
    ) -> None: ...

    def _wait_for_plan_resolution(self, reference: browser_references.PlanRef, state: str) -> None: ...


class BrowserOperationCapability(client_dependencies.Protocol):
    """Define public browser actions shared across capability layers."""

    def switch_session_form_to_resume(
        self, form: browser_references.BrowserSessionFormRef,
    ) -> browser_references.BrowserSessionFormRef:
        """Switch the session form to resume mode."""

    def resume_from_session_form(
        self, form: browser_references.BrowserSessionFormRef, prompt: str,
    ) -> browser_assertions.BrowserSessionResume:
        """Resume a session from its form with the requested prompt."""

    def assert_showing(self, session: runtime_dependencies.SessionRef) -> None:
        """Check that the requested session is visible."""


def running_elapsed_at_least(timer: client_dependencies.Locator, seconds: int) -> bool | None:
    """Return true when the visible timer reaches the required duration.

    Returns:
        True when the visible timer reaches the required duration.

    """
    if not timer.count():
        return None
    return True if browser_usage.duration_seconds(timer.inner_text()) >= seconds else None


def assert_completed_operation_elapsed(block: client_dependencies.Locator, seconds: int, timeout_ms: float) -> None:
    """Verify a completed operation block has the required elapsed time.

    Raises:
        AssertionError: If elapsed time is not visible or is below the required value.

    """
    elapsed_text = block.locator(".cqt")
    browser_expectation(elapsed_text).to_be_visible(timeout=timeout_ms)
    elapsed = browser_usage.duration_seconds(elapsed_text.inner_text())
    if elapsed < seconds:
        msg = f"browser completed operation time is {elapsed} seconds, not at least {seconds}"
        raise AssertionError(msg)


def default_model_usage_window(
    rows: standard_dependencies.Sequence[model_dependencies.UsageRowResponse], harness: str, model: str,
) -> tuple[model_dependencies.UsageRowResponse, model_dependencies.UsageWindowResponse] | None:
    """Select one default model window, or wait while no row exists.

    Returns:
        The usage row and model window, or None while a usable result is unavailable.

    """
    browser_capabilities.raise_usage_refresh_failure(rows)
    if any(row.collection_error is not None for row in rows):
        return None
    row = browser_capabilities.default_harness_row(rows, harness)
    return None if row is None else browser_usage.default_model_window(row, model)


def assert_rendered_usage_window(
    page: client_dependencies.Page,
    row: model_dependencies.UsageRowResponse,
    model_window: model_dependencies.UsageWindowResponse,
) -> None:
    """Verify the dashboard shows one model and weekly usage window.

    Raises:
        AssertionError: If displayed usage does not match or weekly reset information is absent.

    """
    account = browser_capabilities.account_locator(page, row.display_name)
    browser_expectation(account).to_have_count(1)
    model_bar = browser_capabilities.usage_bar_locator(page, account, model_window.label)
    browser_expectation(model_bar).to_have_count(1)
    browser_expectation(model_bar.locator(".upct")).to_have_text(f"{model_window.used_percent}%")
    browser_expectation(page.locator(".usage-collection-error")).to_have_count(0)
    weekly = _weekly_usage_window(row)
    if weekly is None or weekly.resets_at is None:
        msg = f"account {row.display_name!r} has no weekly reset information"
        raise AssertionError(msg)
    weekly_bar = browser_capabilities.usage_bar_locator(page, account, weekly.label)
    browser_expectation(weekly_bar.locator(".ureset")).to_contain_text("resets")
