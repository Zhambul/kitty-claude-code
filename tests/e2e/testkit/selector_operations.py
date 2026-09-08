# Copyright (c) 2026 Zhambyl Yermagambet
"""Select stable file and skill references."""

from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING

from api.sessiondata.models.entry import FileBodyResponse
from domain.entry_base import RunState
from tests.e2e.testkit import references as refs
from tests.e2e.testkit.selector_common import _one, belongs_to_turn

if TYPE_CHECKING:
    from sdk.client import SessionWatch
    from sdk.state import SessionSnapshot


def _find_file_operation(
    snapshot: SessionSnapshot,
    turn_reference: refs.TurnRef,
    path: str,
    action: str,
) -> refs.FileOperationRef | None:
    candidates = [
        entry
        for entry in snapshot.entries
        if belongs_to_turn(
            snapshot,
            turn_reference,
            turn_id=entry.turn_id,
            cursor=entry.cursor,
        )
        and isinstance(entry.body, FileBodyResponse)
        and entry.body.path == path
        and entry.body.action == action
    ]
    file_entry = _one(candidates, f"{action} file operation for {path!r}")
    if file_entry is None:
        return None
    return refs.FileOperationRef(
        snapshot.session_reference,
        file_entry.entry_id,
        file_entry.actor_id,
    )


def file_operation(
    watch: SessionWatch,
    *,
    turn_reference: refs.TurnRef,
    path: str,
    action: str,
    timeout: float,
) -> refs.FileOperationRef:
    """Find one file operation in a turn.

    Returns:
        The file operation reference.

    """
    return watch.wait(
        f"one {action} file operation for {path!r}",
        partial(
            _find_file_operation,
            turn_reference=turn_reference,
            path=path,
            action=action,
        ),
        timeout=timeout,
    )


def _find_skill(
    snapshot: SessionSnapshot,
    turn_reference: refs.TurnRef,
    exact_name: str,
) -> refs.SkillRef | None:
    candidates = [
        skill_state
        for skill_state in snapshot.skills()
        if belongs_to_turn(
            snapshot,
            turn_reference,
            turn_id=skill_state.turn_id,
            cursor=skill_state.started_cursor,
        )
        and skill_state.name.casefold() == exact_name.casefold()
    ]
    selectable = [candidate for candidate in candidates if candidate.state is not RunState.FAILED]
    skill_state = _one(selectable, f"non-failed skill named {exact_name!r}")
    if skill_state is None:
        return None
    return refs.SkillRef(snapshot.session_reference, skill_state.skill_id)


def skill(
    watch: SessionWatch,
    *,
    turn_reference: refs.TurnRef,
    exact_name: str,
    timeout: float,
) -> refs.SkillRef:
    """Find one skill use in a turn.

    Returns:
        The skill reference.

    """
    return watch.wait(
        f"one skill named {exact_name!r}",
        partial(
            _find_skill,
            turn_reference=turn_reference,
            exact_name=exact_name,
        ),
        timeout=timeout,
    )
