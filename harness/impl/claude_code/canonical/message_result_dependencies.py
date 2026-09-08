# Copyright (c) 2026 Zhambyl Yermagambet
"""Expose result translation dependencies."""

from dataclasses import replace as replace

from domain import (
    event_base as event_base,
    event_conversation as event_conversation,
    ids as ids,
    messaging as messaging,
)
from harness.impl.claude_code.canonical import (
    records as records,
    support as support,
    toolcalls as toolcalls,
    transcript as transcript,
    turns as turns,
)
from harness.models import raw_event_builders as raw_event_builders
