# Copyright (c) 2026 Zhambyl Yermagambet
"""Check work notices and deadline waits."""

from __future__ import annotations

from contextlib import ExitStack
from threading import Event, Thread

from core.work_queue import WorkKind, WorkQueue

IDLE_CHECK_SECONDS = 0.7
SOURCE_DEADLINE_SECONDS = 0.02
LATER_DEADLINE_SECONDS = 0.03


def test_work_notices_survive_processing() -> None:
    """Combine repeated notices without losing a notice during processing."""
    queue = WorkQueue()
    queue.put(WorkKind.RAW)
    queue.put(WorkKind.RAW)
    assert queue.take() == {WorkKind.RAW}
    queue.put(WorkKind.RAW)
    queue.put(WorkKind.CANONICAL)
    assert queue.take() == {WorkKind.RAW, WorkKind.CANONICAL}


def test_idle_queue_waits_until_close() -> None:
    """An idle queue must not return for an empty periodic check."""
    queue = WorkQueue()
    returned = Event()

    worker = Thread(target=_wait_until_closed, args=(queue, returned))
    worker.start()
    with ExitStack() as cleanup:
        cleanup.callback(worker.join, 2)
        cleanup.callback(queue.close)
        assert not returned.wait(IDLE_CHECK_SECONDS)
    assert returned.is_set()


def _wait_until_closed(queue: WorkQueue, returned: Event) -> None:
    assert queue.take() == set()
    returned.set()


def test_deadline_survives_an_earlier_notice() -> None:
    """An immediate input must not cancel a required future check."""
    queue = WorkQueue()
    queue.schedule(WorkKind.SOURCES, SOURCE_DEADLINE_SECONDS)
    queue.put(WorkKind.SOURCES)
    assert queue.take() == {WorkKind.SOURCES}
    assert queue.take() == {WorkKind.SOURCES}


def test_independent_deadlines_for_the_same_stage() -> None:
    """An earlier interrupt must not remove a later interrupt deadline."""
    queue = WorkQueue()
    queue.schedule(WorkKind.SOURCES, 0, key="first")
    queue.schedule(WorkKind.SOURCES, LATER_DEADLINE_SECONDS, key="second")
    assert queue.take() == {WorkKind.SOURCES}
    assert queue.take() == {WorkKind.SOURCES}
