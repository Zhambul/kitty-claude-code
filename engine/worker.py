# Copyright (c) 2026 Zhambyl Yermagambet
"""Run engine stages only after an input notice or a known deadline."""

from contextlib import closing
from functools import partial
from pathlib import Path
from threading import Event

from audit.failures import FailureContext
from core.input_events import InputEvents
from core.work_queue import WorkKind, WorkQueue
from engine.interpret.loop import Interpreter
from engine.interpret.output_source import MAXIMUM_LIFETIME_SECONDS
from engine.react.loop import ReactionLoop


class EngineWorker:
    """Own one ordered worker and its external input subscriptions."""

    def __init__(
        self,
        interpreter: Interpreter,
        reaction_loop: ReactionLoop,
        work_queue: WorkQueue,
        profiles: tuple[Path, ...],
    ) -> None:
        """Connect input notices to one ordered worker."""
        self.interpreter = interpreter
        self.reaction_loop = reaction_loop
        self.work_queue = work_queue
        changed = partial(work_queue.put, WorkKind.SOURCES)
        self.inputs = InputEvents(changed, profiles)
        interpreter.puller.watch_files = self.inputs.watch_files
        interpreter.puller.retry = partial(work_queue.schedule, WorkKind.SOURCES, 1.0, key="source retry")

    def run(self, stop_event: Event) -> None:
        """Drain persisted work at startup, then wait for notices."""
        self.inputs.start()
        for kind in WorkKind:
            self.work_queue.put(kind)
        with closing(self.inputs):
            while not stop_event.is_set():
                pending = self.work_queue.take()
                if not pending:
                    return
                self._process(pending, stop_event)

    def stop(self) -> None:
        """Release the worker's idle wait."""
        self.work_queue.close()

    def _process(self, pending: set[WorkKind], stop_event: Event) -> None:
        for kind in WorkKind:
            if kind not in pending or stop_event.is_set():
                continue
            try:
                self._stage(kind, stop_event)
            except Exception:  # noqa: BLE001 -- Record worker failures and retry pending work.
                self.interpreter.failures.record("engine work", FailureContext())
                self.work_queue.schedule(kind, 1.0, key="retry")

    def _stage(self, work_kind: WorkKind, stop_event: Event) -> None:
        if work_kind is WorkKind.SOURCES:
            self._subscriptions()
            self.interpreter.read_sources()
            self._expiry_deadline()
            return
        if work_kind is WorkKind.CANONICAL:
            self.reaction_loop.drain(stop_event.is_set)
            return
        step = self.interpreter.translation.translate
        while not stop_event.is_set():
            if not step():
                return

    def _subscriptions(self) -> None:
        dependencies = self.interpreter.dependencies
        sessions = dependencies.repositories.sessions.watchable()
        outputs = tuple(
            following
            for session in sessions
            for following in dependencies.repositories.shell_output.find_for_session(session.session_id)
        )
        self.inputs.update(
            {Path(session.source_reference).resolve().parent for session in sessions},
            {Path(following.source_path).resolve() for following in outputs},
        )
        self.inputs.watch_processes({
            session.harness_process_id for session in sessions if session.harness_process_id is not None
        })

    def _expiry_deadline(self) -> None:
        dependencies = self.interpreter.dependencies
        oldest = dependencies.repositories.shell_output.oldest_created_at()
        if oldest is not None:
            delay = oldest + MAXIMUM_LIFETIME_SECONDS - dependencies.runtime.clock()
            self.work_queue.schedule(WorkKind.SOURCES, delay, key="output expiry")
