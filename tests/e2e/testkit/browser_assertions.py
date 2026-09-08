# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide browser assertions."""

from __future__ import annotations

from tests.e2e.testkit import (
    browser_client_dependencies as client_dependencies,
    browser_model_dependencies as model_dependencies,
    browser_runtime_dependencies as runtime_dependencies,
    browser_standard_dependencies as standard_dependencies,
    references as browser_references,
)

browser_expectation = model_dependencies.expect
regular_expressions = standard_dependencies.re


def assert_mixed_background(locator: client_dependencies.Locator, css_variable: str, percentage: int) -> None:
    """Verify a mixed CSS background resolves to the expected color."""
    actual, expected = locator.evaluate(
        (
            "(element, input) => {\n          const probe = "
            "document.createElement('div');\n          probe.style.background = "
            "`color-mix(in srgb, var(${input.css_variable}) ${input.percentage}%, "
            "transparent)`;\n          element.append(probe);\n          const result = "
            "[\n            getComputedStyle(element).backgroundColor,\n            "
            "getComputedStyle(probe).backgroundColor,\n          ];\n          "
            "probe.remove();\n          return result;\n        }"
        ),
        {"css_variable": css_variable, "percentage": percentage},
    )
    assert actual == expected
    assert actual not in {"transparent", "rgba(0, 0, 0, 0)"}


def shell_command(snapshot: runtime_dependencies.SessionSnapshot, reference: browser_references.ShellRef) -> str:
    """Return the command for one shell reference.

    Returns:
        The command for one shell reference.

    Raises:
        AssertionError: If the reference does not match exactly one shell.

    """
    matches = [shell for shell in snapshot.shells() if shell.shell_id == reference.shell_id]
    if len(matches) != 1:
        msg = f"shell {reference.shell_id!r} has {len(matches)} matches"
        raise AssertionError(msg)
    return matches[0].command


def file_operation_path(
    snapshot: runtime_dependencies.SessionSnapshot,
    reference: browser_references.FileOperationRef,
) -> str:
    """Return the path for one file operation reference.

    Returns:
        The path for one file operation reference.

    Raises:
        AssertionError: If the reference does not match exactly one file operation.

    """
    matches = [
        entry.body
        for entry in snapshot.entries
        if entry.entry_id == reference.entry_id and isinstance(entry.body, model_dependencies.FileBodyResponse)
    ]
    if len(matches) != 1:
        msg = f"file operation {reference.entry_id!r} has {len(matches)} matches"
        raise AssertionError(msg)
    return matches[0].path


def assert_file_diff_markers(removed: client_dependencies.Locator, added: client_dependencies.Locator) -> None:
    """Verify the file diff line labels and marker characters."""
    browser_expectation(removed).to_have_attribute("aria-label", regular_expressions.compile("^removed line "))
    browser_expectation(added).to_have_attribute("aria-label", regular_expressions.compile("^added line "))
    browser_expectation(removed.locator(".dm")).to_have_text("\u2212")
    browser_expectation(added.locator(".dm")).to_have_text("+")


def send_text_request(
    page: client_dependencies.Page,
    button: client_dependencies.Locator,
    path: str,
    timeout_ms: float,
) -> None:
    """Send text and verify the dashboard response.

    Raises:
        AssertionError: If the response fails for a reason other than a conflict.

    """
    with page.expect_response(
        lambda response: response.request.method == "POST" and response.url.endswith(path),
        timeout=timeout_ms,
    ) as response_info:
        button.click()
        response = response_info.value
        if not response.ok and response.status != standard_dependencies.HTTPStatus.CONFLICT:
            msg = f"browser send returned HTTP {response.status}"
            raise AssertionError(msg)


@standard_dependencies.dataclass(frozen=True)
class BrowserSessionStart:
    """Keep the session and first turn created through the browser."""

    session: runtime_dependencies.SessionRef
    turn: browser_references.TurnRef


@standard_dependencies.dataclass(frozen=True)
class BrowserSessionResume:
    """Keep the session, continuation, and turn created on resume."""

    session: runtime_dependencies.SessionRef
    continuation: browser_references.SessionContinuationRef
    turn: browser_references.TurnRef
