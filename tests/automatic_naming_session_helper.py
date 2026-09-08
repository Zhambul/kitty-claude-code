# Copyright (c) 2026 Zhambyl Yermagambet
"""Durable jobs, title safety, and generic naming semantics."""

from harness.impl.codex.plugin import plugin as codex_plugin
from harness.models.session import (
    Session,
)
from tests.automatic_naming_values import ACTOR_ID, SESSION_ID


def session() -> Session:
    """Build the fixed Codex session.

    Returns:
        The session used by automatic naming tests.

    """
    return Session(
        SESSION_ID,
        ACTOR_ID,
        "/test-data/rollout-session-one.jsonl",
        "/test-data",
        plugin=codex_plugin,
    )
