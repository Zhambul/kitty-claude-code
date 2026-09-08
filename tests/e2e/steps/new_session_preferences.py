# Copyright (c) 2026 Zhambyl Yermagambet
"""Steps that save and check global new-session preferences."""

from __future__ import annotations

import time
from functools import partial

from pytest_bdd import parsers, then, when

from sdk.client import BaqylauClient, wait_for


def _new_session_draft_is_saved(client: BaqylauClient, workspace: str, text: str) -> bool | None:
    drafts = [
        draft
        for draft in client.preferences.global_state().preferences.new_session_drafts
        if draft.working_directory == workspace
    ]
    if not drafts:
        return None
    assert len(drafts) == 1, f"workspace {workspace!r} has {len(drafts)} new-session drafts"
    return True if drafts[0].text == text else None


@when(parsers.parse("I save new-session choices for {harness} model {model} and {effort} effort"))
def save_new_session_choices(client: BaqylauClient, workspace: str, harness: str, model: str, effort: str) -> None:
    """Save global new-session choices."""
    client.preferences.save_new_session_choices(workspace=workspace, harness=harness, model=model, effort=effort)


@when(parsers.parse("I save new-session draft '{text}'"))
def save_new_session_draft(client: BaqylauClient, workspace: str, text: str) -> None:
    """Save a global new-session draft."""
    client.preferences.save_new_session_draft(workspace=workspace, text=text, sequence=time.time())


@then(parsers.parse("global new-session choices are {harness} model {model} and {effort} effort"))
def global_new_session_choices_are_saved(
    client: BaqylauClient,
    workspace: str,
    harness: str,
    model: str,
    effort: str,
) -> None:
    """Verify global new-session choices."""
    found = client.preferences.global_state().preferences.new_session
    actual_choices = (found.working_directory, found.harness, found.model, found.effort)
    assert actual_choices == (workspace, harness, model, effort)


@then(parsers.parse("global new-session draft is '{text}'"))
def global_new_session_draft_is_saved(client: BaqylauClient, workspace: str, text: str) -> None:
    """Verify the global new-session draft."""
    wait_for(
        f"new-session draft for workspace {workspace!r}",
        partial(_new_session_draft_is_saved, client, workspace, text),
        timeout=5,
    )
