# Copyright (c) 2026 Zhambyl Yermagambet
"""Find work that is open at a session-close boundary."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from domain.entries import SessionEntry
from domain.entry_conversation import TurnFinishedBody, TurnStartedBody
from domain.entry_lifecycle import AssignmentFinishedBody, AssignmentStartedBody
from domain.entry_shells import ShellFinishedBody, ShellStartedBody
from domain.ids import AssignmentId, ShellId, TurnId
from domain.work_state import OpenWorkKind
from harness.models.control_observations import SessionCloseWorkObservation

if TYPE_CHECKING:
    from collections.abc import Mapping


OpenWorkId = TurnId | ShellId | AssignmentId


@dataclass(frozen=True)
class SessionCloseWork:
    """Keep one open entry with its close observation."""

    entry: SessionEntry
    observation: SessionCloseWorkObservation


def open_work(entries: tuple[SessionEntry, ...]) -> tuple[SessionCloseWork, ...]:
    """Return work that has no matching finish entry.

    Returns:
        The open work snapshot.

    """
    turns: dict[OpenWorkId, SessionEntry] = {}
    shells: dict[OpenWorkId, SessionEntry] = {}
    assignments: dict[OpenWorkId, SessionEntry] = {}
    for entry in entries:
        _update_open_work(entry, turns, shells, assignments)
    return (
        *_work_observations(OpenWorkKind.TURN, turns),
        *_work_observations(OpenWorkKind.SHELL, shells),
        *_work_observations(OpenWorkKind.ASSIGNMENT, assignments),
    )


def _update_open_work(
    session_entry: SessionEntry,
    turns: dict[OpenWorkId, SessionEntry],
    shells: dict[OpenWorkId, SessionEntry],
    assignments: dict[OpenWorkId, SessionEntry],
) -> None:
    _update_open_turn(session_entry, turns)
    _update_open_shell(session_entry, shells)
    _update_open_assignment(session_entry, assignments)


def _update_open_turn(session_entry: SessionEntry, turns: dict[OpenWorkId, SessionEntry]) -> None:
    body = session_entry.body
    if isinstance(body, TurnStartedBody) and session_entry.turn_id is not None:
        turns[session_entry.turn_id] = session_entry
    elif isinstance(body, TurnFinishedBody) and session_entry.turn_id is not None:
        turns.pop(session_entry.turn_id, None)


def _update_open_shell(session_entry: SessionEntry, shells: dict[OpenWorkId, SessionEntry]) -> None:
    body = session_entry.body
    if isinstance(body, ShellStartedBody):
        shells[body.shell_id] = session_entry
    elif isinstance(body, ShellFinishedBody):
        shells.pop(body.shell_id, None)


def _update_open_assignment(
    session_entry: SessionEntry,
    assignments: dict[OpenWorkId, SessionEntry],
) -> None:
    body = session_entry.body
    if isinstance(body, AssignmentStartedBody):
        assignments[body.assignment_id] = session_entry
    elif isinstance(body, AssignmentFinishedBody):
        assignments.pop(body.assignment_id, None)


def _work_observations(
    open_work_kind: OpenWorkKind,
    open_items: Mapping[OpenWorkId, SessionEntry],
) -> tuple[SessionCloseWork, ...]:
    return tuple(
        SessionCloseWork(
            entry,
            SessionCloseWorkObservation(open_work_kind, subject_id, entry.turn_id),
        )
        for subject_id, entry in open_items.items()
    )
