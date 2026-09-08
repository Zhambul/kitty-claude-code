# Copyright (c) 2026 Zhambyl Yermagambet
"""Build native worker names for E2E work requests."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tests.e2e.testkit.work_models import WorkRequest

WORKER_NAME_CHARACTER_LIMIT = 40
CODEX_HARNESS = "codex"


def worker_name(work_name: str) -> str:
    """Return the native worker name.

    Returns:
        The native worker name.

    """
    words = re.findall(r"[a-z0-9]+", work_name.casefold())
    name_suffix = "_".join(words)[:WORKER_NAME_CHARACTER_LIMIT]
    return f"e2e_{name_suffix}"


def assignment_actor_name(harness: str, work_name: str) -> str:
    """Return the expected native actor name.

    Returns:
        The expected native actor name.

    """
    native_name = worker_name(work_name)
    return native_name.replace("_", " ") if harness == CODEX_HARNESS else native_name


def expected_actor_name(harness: str, request: WorkRequest) -> str | None:
    """Return the expected actor name.

    Returns:
        The actor name, or none when no name is expected.

    """
    if request.exact_actor_name is not None:
        return request.exact_actor_name
    return assignment_actor_name(harness, request.name) if request.named else None
