# Copyright (c) 2026 Zhambyl Yermagambet
"""Own the daemon work that runs beside the request loop."""

from __future__ import annotations

import threading
from contextlib import contextmanager
from dataclasses import dataclass
from typing import TYPE_CHECKING

from api import worker_plans
from app import provider_runtime as runtime_providers, provider_uploads as upload_providers
from app.injection import Instances, resolve
from terminal.contract import TerminalPlugin

if TYPE_CHECKING:
    from collections.abc import Iterator


@dataclass
class _ManagedWorker:
    stop_event: threading.Event
    thread: threading.Thread
    plan: worker_plans.WorkerPlan

    @classmethod
    def start(cls, plan: worker_plans.WorkerPlan) -> _ManagedWorker:
        stop_event = threading.Event()
        thread = threading.Thread(
            target=plan.run,
            args=(stop_event,),
            daemon=True,
            name=plan.name,
        )
        thread.start()
        return cls(stop_event, thread, plan)

    def stop(self) -> None:
        self.stop_event.set()
        if self.plan.stop is not None:
            self.plan.stop()

    def join(self) -> None:
        self.thread.join(timeout=2)


@dataclass
class _WorkerGroup:
    workers: tuple[_ManagedWorker, ...]
    model_terminal: TerminalPlugin
    terminal_plugin: TerminalPlugin

    def close(self) -> None:
        for worker in self.workers:
            worker.stop()
        # A naming call can wait on a native model process. Close its private
        # terminal first so the worker can observe cancellation.
        self.model_terminal.close()
        for worker in self.workers:
            worker.join()
        self.terminal_plugin.close()


def _start_workers(instances: Instances) -> _WorkerGroup:
    managed_workers = tuple(_ManagedWorker.start(plan) for plan in worker_plans.plans(instances))
    return _WorkerGroup(
        managed_workers,
        resolve(instances, runtime_providers.model_terminal),
        resolve(instances, runtime_providers.terminal_plugin),
    )


@contextmanager
def background_workers(instances: Instances) -> Iterator[None]:
    """Start daemon workers on entry and stop them on exit."""
    # Attachments are pruned from the row, not from directory timestamps.
    resolve(instances, upload_providers.uploads).prune()
    workers = _start_workers(instances)
    try:
        yield
    finally:
        workers.close()
