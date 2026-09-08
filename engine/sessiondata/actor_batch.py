# Copyright (c) 2026 Zhambyl Yermagambet
"""Keep the final actor state from a group of committed events."""

from collections.abc import Sequence
from dataclasses import dataclass, field

from domain.actor_state import ActorFacts
from domain.ids import ActorId, SessionId
from engine.sessiondata.contract import AppliedActorListener


@dataclass
class AppliedActorBatch(AppliedActorListener):
    """Combine display changes without dropping history entries."""

    actors: dict[SessionId, dict[ActorId, ActorFacts]] = field(default_factory=dict)

    def applied(self, session_id: SessionId, actors: Sequence[ActorFacts]) -> None:
        """Keep the last committed state for each changed actor."""
        current = self.actors.setdefault(session_id, {})
        current.update((actor.actor_id, actor) for actor in actors)
