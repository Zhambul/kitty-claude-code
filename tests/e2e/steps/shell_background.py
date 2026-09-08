# Copyright (c) 2026 Zhambyl Yermagambet
"""Steps that check background shell work."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pytest_bdd import parsers, then

from tests.e2e.testkit.shell_states import shell, wait_for_output

if TYPE_CHECKING:
    from sdk.client import BaqylauClient
    from sdk.state import SessionSnapshot
    from tests.e2e.testkit.policy import WaitPolicy
    from tests.e2e.testkit.references import Shells


def running_shell_ids(snapshot: SessionSnapshot) -> set[str]:
    """Return the background shell identifiers in a snapshot.

    Returns:
        The identifiers of running background shells.

    """
    return {shell_id for actor in snapshot.session_data.actors for shell_id in actor.background.running_shell_ids}


@then(parsers.parse('command "{name}" becomes a background job'))
def command_becomes_background_job(client: BaqylauClient, shells: Shells, wait_policy: WaitPolicy, name: str) -> None:
    """Wait for a shell command to become a background job."""
    reference = shells.get(name)
    client.sessions.watch(reference.session).wait(
        f"command {name!r} to report that it was backgrounded",
        lambda snapshot: True if shell(snapshot, reference).backgrounded else None,
        timeout=wait_policy.feed,
    )


@then(parsers.parse('job "{name}" is running'))
@then(parsers.parse('monitor "{name}" is running'))
def background_work_is_running(client: BaqylauClient, shells: Shells, wait_policy: WaitPolicy, name: str) -> None:
    """Wait for background work to be running."""
    reference = shells.get(name)
    client.sessions.watch(reference.session).wait(
        f"background work {name!r} to be in the running set",
        lambda snapshot: True if reference.shell_id in running_shell_ids(snapshot) else None,
        timeout=wait_policy.feed,
    )


@then(parsers.parse("job \"{name}\" has output containing '{text}'"))
def job_has_output(client: BaqylauClient, shells: Shells, wait_policy: WaitPolicy, name: str, text: str) -> None:
    """Wait for background job output."""
    wait_for_output(client, shells.get(name), wait_policy, name, text)


@then(parsers.parse("monitor \"{name}\" has event containing '{text}'"))
def monitor_has_event(client: BaqylauClient, shells: Shells, wait_policy: WaitPolicy, name: str, text: str) -> None:
    """Wait for a monitor event."""
    reference = shells.get(name)
    client.sessions.watch(reference.session).wait(
        f"monitor {name!r} event to contain {text!r}",
        lambda snapshot: True if text in shell(snapshot, reference).status else None,
        timeout=wait_policy.background,
    )


@then(parsers.parse('job "{name}" ends'))
@then(parsers.parse('monitor "{name}" ends'))
def background_work_ends(client: BaqylauClient, shells: Shells, wait_policy: WaitPolicy, name: str) -> None:
    """Wait for background work to stop."""
    reference = shells.get(name)
    client.sessions.watch(reference.session).wait(
        f"background work {name!r} to leave the running set",
        lambda snapshot: None if reference.shell_id in running_shell_ids(snapshot) else True,
        timeout=wait_policy.background,
    )
