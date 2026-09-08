# Copyright (c) 2026 Zhambyl Yermagambet
"""Wait for a session scoreboard condition."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from sdk.client import BaqylauClient
from tests.e2e.testkit.policy import WaitPolicy
from tests.e2e.testkit.references import Sessions

if TYPE_CHECKING:
    from collections.abc import Callable

    from sdk.state import SessionSnapshot


@dataclass(frozen=True)
class ScoreWait:
    """Keep the dependencies for one scoreboard wait."""

    client: BaqylauClient
    sessions: Sessions
    policy: WaitPolicy
    session_name: str

    def until(self, description: str, condition: Callable[[SessionSnapshot], bool]) -> None:
        """Wait until the named session meets a scoreboard condition."""
        session = self.sessions.get(self.session_name)
        self.client.sessions.watch(session).wait(
            description,
            lambda snapshot: True if condition(snapshot) else None,
            timeout=self.policy.feed,
        )
