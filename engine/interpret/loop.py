# Copyright (c) 2026 Zhambyl Yermagambet
"""Run the raw-event pull and translation cycle."""

from __future__ import annotations

from audit.failures import CoalescingFailureRecorder, FailureContext
from engine.interpret import dependencies, output_source, resumes, snapshots
from engine.interpret.puller import RawEventPuller
from engine.interpret.translation import TranslationPhase

SHELL_OUTPUT_EXPIRY_INTERVAL_SECONDS = 60.0

TerminalWindowReader = snapshots.TerminalWindowReader
TerminalSnapshotCache = snapshots.TerminalSnapshotCache
TerminalSnapshotSampler = snapshots.TerminalSnapshotSampler
InterpreterRepositories = dependencies.InterpreterRepositories
InterpreterServices = dependencies.InterpreterServices
InterpreterRuntime = dependencies.InterpreterRuntime
InterpreterDependencies = dependencies.InterpreterDependencies


class Interpreter:
    """Run one contained pull and translation cycle at a time."""

    def __init__(self, interpreter_dependencies: InterpreterDependencies) -> None:
        """Initialize the interpreter."""
        self.dependencies = interpreter_dependencies
        self.failures = CoalescingFailureRecorder(
            interpreter_dependencies.services.audit,
            "interpreter",
        )
        self.terminal_snapshots: TerminalSnapshotCache = TerminalSnapshotSampler(
            interpreter_dependencies.runtime.terminal,
        )
        self.puller = RawEventPuller(interpreter_dependencies, self._audit_failure)
        self.translation = TranslationPhase(
            interpreter_dependencies,
            self.terminal_snapshots,
            self._audit_failure,
        )
        self.last_expiration_at: float | None = None

    def tick(self) -> None:
        """Run one interpreter cycle."""
        terminal_windows = self.terminal_snapshots.sample()
        self._expire()
        resumes.discover_resumes(self.dependencies, terminal_windows)
        self.puller.pull(terminal_windows)
        self.translation.terminal_snapshots = self.terminal_snapshots
        self.translation.translate()

    def read_sources(self) -> None:
        """Read sources after a change notice."""
        self.terminal_snapshots.invalidate()
        terminal_windows = self.terminal_snapshots.sample()
        output_source.expire(self.dependencies.repositories.shell_output, self.dependencies.runtime.clock())
        resumes.discover_resumes(self.dependencies, terminal_windows)
        self.puller.pull(terminal_windows)

    def _audit_failure(
        self,
        where: str,
        failure_context: FailureContext,
    ) -> None:
        self.failures.record(where, failure_context)

    def _expire(self) -> None:
        now = self.dependencies.runtime.clock()
        if self._expiry_is_current(now):
            return
        try:
            output_source.expire(
                self.dependencies.repositories.shell_output,
                now,
            )
        except Exception:  # noqa: BLE001 - Record cleanup failure and continue the source reads.
            self._audit_failure("output expiry", FailureContext())
        else:
            self.last_expiration_at = now

    def _expiry_is_current(self, now: float) -> bool:
        if self.last_expiration_at is None:
            return False
        elapsed = now - self.last_expiration_at
        return 0 <= elapsed < SHELL_OUTPUT_EXPIRY_INTERVAL_SECONDS
