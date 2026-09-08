# Copyright (c) 2026 Zhambyl Yermagambet
"""Actor status background."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from domain import (
    actor_state,
    event_shell,
    outcomes,
)

if TYPE_CHECKING:
    from domain import ids


def _shell_started(
    actor_facts: actor_state.ActorFacts, shell_started: event_shell.ShellStarted,
) -> actor_state.ActorFacts:
    if shell_started.execution == outcomes.ExecutionMode.FOREGROUND:
        return replace(actor_facts, status=actor_state.ActorStatus.EXECUTING)
    counted = replace(
        actor_facts.background,
        monitor_count=(
            actor_facts.background.monitor_count + (shell_started.execution == outcomes.ExecutionMode.MONITOR)
        ),
        background_job_count=(
            actor_facts.background.background_job_count + (shell_started.execution == outcomes.ExecutionMode.BACKGROUND)
        ),
    )
    return replace(
        _with_background(replace(actor_facts, background=counted), shell_started.shell_id),
        status=actor_state.ActorStatus.EXECUTING,
    )


def _with_background(
    actor_facts: actor_state.ActorFacts,
    shell_id: ids.ShellId,
    *,
    counts_as_job: bool = False,
) -> actor_state.ActorFacts:
    """Add a command to the running-background set.

    `counts_as_job` is for the command that MOVED there mid-run: nothing counted
    it at launch, because at launch nobody knew.

    Returns:
        The actor facts.

    """
    background = actor_facts.background
    if shell_id in background.running_shell_ids:
        return actor_facts
    return replace(
        actor_facts,
        background=replace(
            background,
            running_shell_ids=(*background.running_shell_ids, shell_id),
            background_job_count=background.background_job_count + counts_as_job,
        ),
    )


def _without_background(actor_facts: actor_state.ActorFacts, shell_id: ids.ShellId) -> actor_state.ActorFacts:
    return replace(
        actor_facts,
        background=replace(
            actor_facts.background,
            running_shell_ids=tuple(
                running for running in actor_facts.background.running_shell_ids if running != shell_id
            ),
        ),
    )


def _added[Identity](pending: tuple[Identity, ...], identity: Identity) -> tuple[Identity, ...]:
    return pending if identity in pending else (*pending, identity)
