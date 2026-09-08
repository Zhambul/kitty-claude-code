# Copyright (c) 2026 Zhambyl Yermagambet
"""Steps that name and check web fetches."""

from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING

from pytest_bdd import parsers, then, when

from api.sessiondata.models.entry import EntryResponse, WebBodyResponse
from tests.e2e.testkit import selector_web

if TYPE_CHECKING:
    from sdk.client import BaqylauClient
    from sdk.state import SessionSnapshot
    from tests.e2e.testkit.action_contexts import TurnObservationContext
    from tests.e2e.testkit.policy import WaitPolicy
    from tests.e2e.testkit.references import WebFetches, WebFetchRef


def _web_fetch_entry(snapshot: SessionSnapshot, reference: WebFetchRef) -> EntryResponse:
    found = [
        entry
        for entry in snapshot.entries
        if entry.entry_id == reference.entry_id and isinstance(entry.body, WebBodyResponse)
    ]
    if len(found) != 1:
        message = f"web fetch {reference.entry_id!r} has {len(found)} matches"
        raise AssertionError(message)
    return found[0]


def _web_fetch_result_contains(
    snapshot: SessionSnapshot,
    reference: WebFetchRef,
    text: str,
) -> bool | None:
    entry = _web_fetch_entry(snapshot, reference)
    assert isinstance(entry.body, WebBodyResponse)
    result = entry.body.result
    return True if result is not None and text in result.text else None


@when(parsers.parse('I name the web fetch in work "{work_name}" for URL \'{url}\' "{fetch_name}"'))
def name_web_fetch(
    web_fetch_observation_context: TurnObservationContext[WebFetchRef],
    work_name: str,
    url: str,
    fetch_name: str,
) -> None:
    """Name one web fetch that belongs to a work turn."""
    turn = web_fetch_observation_context.turns.get(work_name)
    web_fetch_observation_context.references.bind(
        fetch_name,
        selector_web.web_fetch(
            web_fetch_observation_context.client.sessions.watch(turn.session),
            turn_reference=turn,
            url=url,
            timeout=web_fetch_observation_context.wait_policy.feed,
        ),
    )


@then(parsers.parse('web fetch "{name}" has state {state}'))
def web_fetch_has_state(client: BaqylauClient, web_fetches: WebFetches, name: str, state: str) -> None:
    """Verify the state of one named web fetch."""
    reference = web_fetches.get(name)
    entry = _web_fetch_entry(client.sessions.snapshot(reference.session), reference)
    assert isinstance(entry.body, WebBodyResponse)
    assert entry.body.state == state


@then(parsers.parse("web fetch \"{name}\" has result containing '{text}'"))
def web_fetch_has_result(
    client: BaqylauClient,
    web_fetches: WebFetches,
    wait_policy: WaitPolicy,
    name: str,
    text: str,
) -> None:
    """Verify a named web fetch result contains text."""
    reference = web_fetches.get(name)
    client.sessions.watch(reference.session).wait(
        f"web fetch {name!r} result to contain {text!r}",
        partial(_web_fetch_result_contains, reference=reference, text=text),
        timeout=wait_policy.feed,
    )
