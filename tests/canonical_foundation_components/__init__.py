# Copyright (c) 2026 Zhambyl Yermagambet
"""Expose component namespaces used by canonical foundation tests."""

from engine.interpret import (
    interrupts as interrupts,
    liveness as liveness,
    loop as loop,
    reactions as reactions,
    translators as translators,
)
from engine.sessiondata import actors as actors, entries as entries, session as session
from harness.models import launch as launch, raw_events as raw_events
from repository.mapper import documents as documents
from repository.model import facts as facts
from terminal import adapter as adapter
from terminal.panes import reaction as reaction
from tests import terminal_value_models as terminal_value_models
