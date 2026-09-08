# Copyright (c) 2026 Zhambyl Yermagambet
"""The last model and effort a translator saw, so that a repeat is not a change.

Both harnesses report the CURRENT model on every model response and the current
effort on every mid-turn hook. Recorded verbatim that produced 6,642 stored
`model.changed` rows on one machine, nearly all of them saying exactly what the
row before them said — and every one of them with `previous` empty, because a
single observation cannot know what it replaced.

A change event has to carry a change. That needs memory, and it cannot be the
store's: the store dedups by event id forever, which cannot represent a switch
to B and back to A.

Shared by both harness translators, and shared HERE for the same reason
`canonical_event` is: it is a rule about the facts, not about any harness's
grammar. Memory is per process — the first observation after a restart is a
change with no previous, which is one event per restart rather than one per
response.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from domain.event_session import EffortChanged, ModelChanged

if TYPE_CHECKING:
    from domain.ids import ActorId, SessionId
    from domain.references import ModelReference
    from domain.work_state import EffortChangeReason, ModelChangeReason

type SelectionStates[SelectionStateT] = dict[tuple[str, str], SelectionStateT]


def selection_key(session_id: SessionId, actor_id: ActorId) -> tuple[str, str]:
    """Return the selection state key.

    Returns:
        The session and actor key.

    """
    return str(session_id), str(actor_id)


def retained_states[SelectionStateT](
    selection_states: SelectionStates[SelectionStateT],
    session_key: str,
) -> SelectionStates[SelectionStateT]:
    """Remove state for one session.

    Returns:
        State for all other sessions.

    """
    remaining_states: SelectionStates[SelectionStateT] = {}
    for state_key, selection_state in selection_states.items():
        if state_key[0] == session_key:
            continue
        remaining_states[state_key] = selection_state
    return remaining_states


class SelectionSemantics:
    """Represent selection semantics."""

    def __init__(self) -> None:
        """Initialize the object."""
        self._models: dict[tuple[str, str], tuple[ModelReference, str]] = {}
        self._efforts: dict[tuple[str, str], str] = {}

    def model(
        self,
        session_id: SessionId,
        actor_id: ActorId,
        model_reference: ModelReference,
        model_change_reason: ModelChangeReason,
        equivalence_key: str,
    ) -> ModelChanged | None:
        """Return the model.

        The switch this observation reports, or None when it reports no switch.

                The adapter supplies the key used to compare its aliases and resolved
                names. That vendor rule does not leak into the canonical reference.

        Returns:
            Model.

        """
        key = selection_key(session_id, actor_id)
        previous_observation = self._models.get(key)
        previous_model = None
        if previous_observation is not None:
            if previous_observation[1] == equivalence_key:
                return None
            previous_model = previous_observation[0]
        self._models[key] = (model_reference, equivalence_key)
        return ModelChanged(previous_model, model_reference, model_change_reason)

    def effort(
        self,
        session_id: SessionId,
        actor_id: ActorId,
        current: str,
        effort_change_reason: EffortChangeReason,
    ) -> EffortChanged | None:
        """Return the effort.

        Returns:
            Effort.

        """
        key = selection_key(session_id, actor_id)
        previous = self._efforts.get(key)
        if previous == current:
            return None
        self._efforts[key] = current
        return EffortChanged(previous, current, effort_change_reason)

    def release_session(self, session_id: SessionId) -> None:
        """Release the last reported selections for one finished session."""
        session_key = str(session_id)
        self._models = retained_states(self._models, session_key)
        self._efforts = retained_states(self._efforts, session_key)
