# Copyright (c) 2026 Zhambyl Yermagambet
"""Start test workers and release them when a test leaves its scope."""

from collections.abc import Callable, Iterator
from contextlib import ExitStack, contextmanager
from threading import Event, Thread


@contextmanager
def running_worker(
    run: Callable[[Event], None],
    stop: Callable[[], None],
) -> Iterator[Thread]:
    """Run a worker and stop it on normal exit or test failure.

    Yields:
        The worker thread, which the caller can check after shutdown.

    """
    cancelled = Event()
    thread = Thread(target=run, args=(cancelled,))
    with ExitStack() as cleanup:
        thread.start()
        cleanup.callback(thread.join, 1)
        cleanup.callback(stop)
        cleanup.callback(cancelled.set)
        yield thread
