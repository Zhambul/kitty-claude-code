# Copyright (c) 2026 Zhambyl Yermagambet
"""Pull raw events from all sources for watchable sessions."""

from __future__ import annotations

import dataclasses
from pathlib import Path
from typing import TYPE_CHECKING

from audit.failures import FailureContext
from engine.interpret import liveness, output_source
from engine.interpret.interrupts import PendingInterruptSource
from harness.contract import HarnessRawEventSource
from harness.models.session import Session

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping

    from engine.interpret.dependencies import InterpreterDependencies
    from harness.contract import TerminalWindows


@dataclasses.dataclass(frozen=True)
class SessionSourceBatch:
    """Hold all pull sources for one session and one cycle."""

    session: Session
    sources: tuple[HarnessRawEventSource, ...]


def _watch_paths(batches: list[SessionSourceBatch]) -> set[Path]:
    paths: set[Path] = set()
    for batch in batches:
        for source in batch.sources:
            paths.update(Path(path).resolve() for path in source.watch_paths())
    return paths


class RawEventPuller:
    """Pull and record raw events without stopping on one source failure."""

    def __init__(
        self,
        interpreter_dependencies: InterpreterDependencies,
        audit_failure: Callable[[str, FailureContext], None],
    ) -> None:
        """Initialize the puller."""
        self.dependencies = interpreter_dependencies
        self.audit_failure = audit_failure
        self.process_probe = liveness.ProcessProbe()
        self.watch_files: Callable[[set[Path]], None] = lambda _paths: None
        self.retry: Callable[[], None] = lambda: None

    def pull(self, terminal_windows: TerminalWindows) -> None:
        """Pull all watchable session sources."""
        batches = self._source_batches(terminal_windows)
        self.watch_files(_watch_paths(batches))
        identities = tuple(
            dict.fromkeys(
                source.source_identity for batch in batches for source in batch.sources if source.source_identity
            ),
        )
        try:
            positions = self.dependencies.repositories.raw_events.latest_positions(identities)
        except Exception:  # noqa: BLE001 - Record a repository failure and request a retry.
            self.retry()
            for batch in batches:
                self.audit_failure(
                    "resume positions",
                    FailureContext(session_id=batch.session.session_id),
                )
            return
        for batch in batches:
            self._pull_sources(batch, positions)

    def _source_batches(
        self,
        terminal_windows: TerminalWindows,
    ) -> list[SessionSourceBatch]:
        batches: list[SessionSourceBatch] = []
        for session in self.dependencies.repositories.sessions.watchable():
            try:
                sources = self._sources_for_session(session, terminal_windows)
            except Exception:  # noqa: BLE001 - Record a plugin failure and continue with other sessions.
                self.retry()
                self.audit_failure(
                    "source construction",
                    FailureContext(session_id=session.session_id),
                )
                continue
            batches.append(SessionSourceBatch(session, sources))
        return batches

    def _sources_for_session(
        self,
        session: Session,
        terminal_windows: TerminalWindows,
    ) -> tuple[HarnessRawEventSource, ...]:
        if session.plugin is None:
            message = f"session has no attached harness plugin: {session.session_id}"
            raise ValueError(message)
        return (
            self._liveness_source(session, terminal_windows),
            *session.plugin.sources.for_session(session),
            *output_source.sources_for_session(
                self.dependencies.repositories.shell_output,
                session.session_id,
            ),
            PendingInterruptSource(session, self.dependencies.services.interrupts),
        )

    def _liveness_source(
        self,
        session: Session,
        terminal_windows: TerminalWindows,
    ) -> HarnessRawEventSource:
        if session.harness_process_id is not None:
            return liveness.SessionLivenessSource(session, self.process_probe, terminal_windows)
        if self.dependencies.runtime.terminal is not None:
            return liveness.SessionWindowLivenessSource(session, terminal_windows)
        message = f"session has no liveness source: {session.session_id}"
        raise ValueError(message)

    def _pull_sources(
        self,
        session_source_batch: SessionSourceBatch,
        positions: Mapping[str, str],
    ) -> None:
        for source in session_source_batch.sources:
            self._pull_source(
                session_source_batch.session,
                source,
                positions.get(source.source_identity),
            )

    def _pull_source(
        self,
        session: Session,
        harness_raw_event_source: HarnessRawEventSource,
        after_position: str | None,
    ) -> None:
        try:
            _read_and_record(
                self.dependencies,
                harness_raw_event_source,
                after_position,
            )
        except Exception:  # noqa: BLE001 - Record a source failure and let other sources run.
            self.retry()
            self.audit_failure(
                "source read",
                FailureContext(
                    session_id=session.session_id,
                    source_identity=getattr(harness_raw_event_source, "source_identity", ""),
                    source=type(harness_raw_event_source).__name__,
                ),
            )


def _read_and_record(
    interpreter_dependencies: InterpreterDependencies,
    harness_raw_event_source: HarnessRawEventSource,
    after_position: str | None,
) -> None:
    while raw_events := harness_raw_event_source.read(after_position):
        interpreter_dependencies.repositories.raw_events.record(raw_events)
        next_position = raw_events[-1].source_position
        if next_position == after_position:
            return
        after_position = next_position
