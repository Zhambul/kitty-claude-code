# Copyright (c) 2026 Zhambyl Yermagambet
"""Steps that name and check web searches."""

from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING

from pytest_bdd import parsers, then, when

from api.sessiondata.models.entry import SearchBodyResponse
from tests.e2e.testkit import selector_web

if TYPE_CHECKING:
    from sdk.client import BaqylauClient
    from sdk.state import SessionSnapshot
    from tests.e2e.testkit.action_contexts import TurnObservationContext
    from tests.e2e.testkit.policy import WaitPolicy
    from tests.e2e.testkit.references import Searches, SearchRef


def _search(snapshot: SessionSnapshot, reference: SearchRef) -> SearchBodyResponse:
    found = [
        entry.body
        for entry in snapshot.entries
        if entry.entry_id == reference.entry_id and isinstance(entry.body, SearchBodyResponse)
    ]
    if len(found) != 1:
        message = f"search {reference.entry_id!r} has {len(found)} matches"
        raise AssertionError(message)
    return found[0]


def _search_result_contains(
    snapshot: SessionSnapshot,
    reference: SearchRef,
    text: str,
) -> bool | None:
    result = _search(snapshot, reference).result
    return True if result is not None and text in result.text else None


@when(parsers.parse('I name the search in work "{work_name}" with query containing \'{query}\' "{search_name}"'))
def name_search(
    search_observation_context: TurnObservationContext[SearchRef],
    work_name: str,
    query: str,
    search_name: str,
) -> None:
    """Name one search that belongs to a work turn."""
    turn = search_observation_context.turns.get(work_name)
    search_observation_context.references.bind(
        search_name,
        selector_web.search(
            search_observation_context.client.sessions.watch(turn.session),
            turn_reference=turn,
            query_contains=query,
            timeout=search_observation_context.wait_policy.feed,
        ),
    )


@then(parsers.parse('search "{name}" has state {state}'))
def search_has_state(client: BaqylauClient, searches: Searches, name: str, state: str) -> None:
    """Verify the state of one named search."""
    reference = searches.get(name)
    assert _search(client.sessions.snapshot(reference.session), reference).state == state


@then(parsers.parse("search \"{name}\" has result containing '{text}'"))
def search_has_result(
    client: BaqylauClient,
    searches: Searches,
    wait_policy: WaitPolicy,
    name: str,
    text: str,
) -> None:
    """Verify a named search result contains text."""
    reference = searches.get(name)
    client.sessions.watch(reference.session).wait(
        f"search {name!r} result to contain {text!r}",
        partial(_search_result_contains, reference=reference, text=text),
        timeout=wait_policy.feed,
    )
