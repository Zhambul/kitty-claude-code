# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the canonical-event reaction loop."""

import time
from collections.abc import Callable

from audit.failures import CoalescingFailureRecorder
from engine.react.dependencies import ReactionLoopDependencies as ReactionLoopDependencies
from engine.react.loop_effects import ReactionLoopEffects
from engine.react.loop_materialization import ReactionLoopMaterialization
from engine.react.loop_runtime import ReactionLoopRuntime


class ReactionLoop(ReactionLoopRuntime, ReactionLoopEffects, ReactionLoopMaterialization):
    """React to committed facts and materialize their read-model state."""

    def __init__(
        self,
        reaction_loop_dependencies: ReactionLoopDependencies,
        clock: Callable[[], float] = time.time,
    ) -> None:
        """Initialize the object."""
        self.dependencies = reaction_loop_dependencies
        self.failures = CoalescingFailureRecorder(reaction_loop_dependencies.audit_recorder, "reactions")
        self.clock = clock
