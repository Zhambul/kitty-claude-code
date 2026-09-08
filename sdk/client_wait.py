# Copyright (c) 2026 Zhambyl Yermagambet
"""Split SDK client implementation."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

    from sdk import state


class WaitTimeoutError(AssertionError):
    """Represent wait timeout."""


def wait_for[WaitResultT](
    description: str | Callable[[], str],
    read: Callable[[], WaitResultT | None],
    *,
    timeout: float,
    interval: float = 0.5,
) -> WaitResultT:
    """Wait for.

    Returns:
        The t.

    Raises:
        WaitTimeoutError: If the wait time limit expires.

    """
    deadline = time.monotonic() + timeout
    while True:
        found = read()
        if found is not None and found is not False:
            return found
        if time.monotonic() >= deadline:
            detail = description() if callable(description) else description
            message = f"timed out after {timeout:.0f}s waiting for {detail}"
            raise WaitTimeoutError(message)
        time.sleep(interval)


def _health_wait_description(last_error: list[str]) -> str:
    error_text = last_error[-1] if last_error else "none"
    return f"the application health response; last error: {error_text}"


def _finished_wait_description(snapshot: state.SessionSnapshot, session_id: str) -> str:
    session_state = snapshot.session_data.session.state
    actor_states = [actor.state for actor in snapshot.session_data.actors]
    return (
        f"session {session_id!r} and all its actors to finish; "
        f"session state is {session_state!r}, actor states are {actor_states}"
    )
