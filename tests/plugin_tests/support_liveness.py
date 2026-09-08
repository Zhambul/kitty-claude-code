# Copyright (c) 2026 Zhambyl Yermagambet
"""Quiet liveness fixture for plugin tests."""

from engine.interpret.liveness import ProcessProbe
from harness import contract as harness_contract
from harness.models import raw_events as raw_event_models
from harness.models.session import Session


class QuietLiveness:
    """Keep fixture sessions open during unrelated tests."""

    def __init__(
        self,
        session: Session,
        probe: ProcessProbe,
        terminal_windows: harness_contract.TerminalWindows = (),
    ) -> None:
        """Keep the session inputs and record read positions."""
        self.source_identity = f"test:liveness:{session.session_id}"
        self.probe = probe
        self.terminal_windows = terminal_windows
        self.read_positions: list[str | None] = []

    def read(self, after_position: str | None) -> tuple[raw_event_models.RawEvent, ...]:
        """Return no liveness events.

        Returns:
            No liveness events.

        """
        self.read_positions.append(after_position)
        return ()

    def watch_paths(self) -> tuple[str, ...]:
        """Return no file inputs.

        Returns:
            No file inputs.

        """
        return ()
