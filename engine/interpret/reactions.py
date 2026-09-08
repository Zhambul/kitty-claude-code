# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the reactions that update state after a canonical event."""

from engine.interpret.interrupt_reaction import (
    InterruptCanonicalEventReaction as _InterruptCanonicalEventReaction,
)
from engine.interpret.session_reaction import (
    SessionUpsertCanonicalEventReaction as _SessionUpsertCanonicalEventReaction,
)
from engine.interpret.shell_output_reaction import (
    ShellOutputCanonicalEventReaction as _ShellOutputCanonicalEventReaction,
)

InterruptCanonicalEventReaction = _InterruptCanonicalEventReaction
SessionUpsertCanonicalEventReaction = _SessionUpsertCanonicalEventReaction
ShellOutputCanonicalEventReaction = _ShellOutputCanonicalEventReaction
