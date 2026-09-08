# Copyright (c) 2026 Zhambyl Yermagambet
"""Browser coverage for prompt confirmation at the interrupt boundary."""

from __future__ import annotations

import contextlib
import os
from typing import TYPE_CHECKING

import pytest
from playwright.sync_api import Page, Request, expect
from pytest_bdd import parsers, scenarios, then

from tests.e2e.testkit.policy import E2E_SCENARIO_TIMEOUT_SECONDS

if TYPE_CHECKING:
    from tests.e2e.testkit.policy import WaitPolicy

pytestmark = [
    pytest.mark.browser,
    pytest.mark.drift,
    pytest.mark.timeout(E2E_SCENARIO_TIMEOUT_SECONDS),
    pytest.mark.skipif(
        not os.environ.get("BAQYLAU_E2E_BROWSER"),
        reason="real-browser E2E tests are opt-in",
    ),
]

scenarios("../features/send_interrupt.feature")


class _InterruptRequestRecorder:
    """Record browser interrupt requests."""

    def __init__(self, requests: list[str]) -> None:
        self._requests = requests

    def __call__(self, request: Request) -> None:
        if request.method == "POST" and request.url.endswith("/controls/interrupt"):
            self._requests.append(request.url)


@then(parsers.parse("the browser shows confirmed prompt '{text}'"))
def browser_shows_confirmed_prompt(
    page: Page,
    wait_policy: WaitPolicy,
    text: str,
) -> None:
    """Process browser shows confirmed prompt."""
    timeout = round(wait_policy.feed * 1_000)
    expect(
            page.locator(".msg.prompt.pending").filter(has_text=text),
    ).to_have_count(0, timeout=timeout)
    expect(
            page.locator(".msg.prompt:not(.pending):not(.queued)").filter(
            has_text=text,
        ),
    ).to_have_count(1, timeout=timeout)


@then("one idle Escape does not request Stop")
def idle_escape_does_not_request_stop(page: Page) -> None:
    """Process idle escape does not request stop."""
    interrupt_requests: list[str] = []
    recorder = _InterruptRequestRecorder(interrupt_requests)
    page.on("request", recorder)
    with contextlib.ExitStack() as cleanup:
        cleanup.callback(page.remove_listener, "request", recorder)
        page.keyboard.press("Escape")
        page.wait_for_timeout(1_000)
    assert not interrupt_requests, f"idle Escape requested Stop: {interrupt_requests}"
