# Copyright (c) 2026 Zhambyl Yermagambet
"""Steps that check session model, effort, and title metadata."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pytest_bdd import parsers, then

if TYPE_CHECKING:
    from sdk.client import BaqylauClient
    from sdk.state import SessionSnapshot
    from tests.e2e.testkit import policy
    from tests.e2e.testkit.references import Sessions, SessionSpecs


def _lead_model(snapshot: SessionSnapshot) -> str:
    lead = snapshot.lead()
    return lead.model or ""


@then(parsers.parse('session "{name}" reports its configured model'))
def session_reports_model(
    client: BaqylauClient,
    sessions: Sessions,
    session_specs: SessionSpecs,
    name: str,
) -> None:
    """Check the configured model in session metadata."""
    wanted = session_specs.get(name).model.casefold()
    reported = _lead_model(client.sessions.snapshot(sessions.get(name))).casefold()
    assert wanted in reported, f"configured model {wanted!r}, reported model {reported!r}"


@then(parsers.parse('session "{name}" reports model {model}'))
def session_reports_selected_model(
    client: BaqylauClient,
    sessions: Sessions,
    wait_policy: policy.WaitPolicy,
    name: str,
    model: str,
) -> None:
    """Wait for one selected session model."""
    wanted = model.casefold()
    client.sessions.watch(sessions.get(name)).wait(
        f"session {name!r} to report model {model!r}",
        lambda snapshot: True if wanted in _lead_model(snapshot).casefold() else None,
        timeout=wait_policy.feed,
    )


@then(parsers.parse('session "{name}" reports its configured effort'))
def session_reports_effort(
    client: BaqylauClient,
    sessions: Sessions,
    session_specs: SessionSpecs,
    name: str,
) -> None:
    """Check the configured effort in session metadata."""
    wanted = session_specs.get(name).effort
    reported = client.sessions.snapshot(sessions.get(name)).lead().effort
    assert reported == wanted, f"configured effort {wanted!r}, reported effort {reported!r}"


@then(parsers.parse("session \"{name}\" has title '{title}'"))
def session_has_title(
    client: BaqylauClient,
    sessions: Sessions,
    wait_policy: policy.WaitPolicy,
    name: str,
    title: str,
) -> None:
    """Wait for one session title."""
    client.sessions.watch(sessions.get(name)).wait(
        f"session {name!r} to have title {title!r}",
        lambda snapshot: True if snapshot.session_data.session.title == title else None,
        timeout=wait_policy.feed,
    )


@then(parsers.parse('session "{name}" has a non-empty native title'))
def session_has_non_empty_native_title(
    client: BaqylauClient,
    sessions: Sessions,
    wait_policy: policy.WaitPolicy,
    name: str,
) -> None:
    """Wait for a non-empty native title."""
    client.sessions.watch(sessions.get(name)).wait(
        f"session {name!r} to have a non-empty native title",
        lambda snapshot: True if (snapshot.session_data.session.title or "").strip() else None,
        timeout=wait_policy.feed,
    )


@then(parsers.parse('session "{name}" reports effort {effort}'))
def session_reports_exact_effort(
    client: BaqylauClient,
    sessions: Sessions,
    wait_policy: policy.WaitPolicy,
    name: str,
    effort: str,
) -> None:
    """Wait for one exact session effort."""
    client.sessions.watch(sessions.get(name)).wait(
        f"session {name!r} to report effort {effort!r}",
        lambda snapshot: True if snapshot.lead().effort == effort else None,
        timeout=wait_policy.feed,
    )
