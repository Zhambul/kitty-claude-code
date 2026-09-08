# Copyright (c) 2026 Zhambyl Yermagambet
"""Define reaction-loop component requirements."""

from typing import Protocol

from audit.failures import CoalescingFailureRecorder
from engine.react.dependencies import ReactionLoopDependencies


class ReactionLoopContext(Protocol):
    """Provide shared reaction-loop state and operations."""

    dependencies: ReactionLoopDependencies
    failures: CoalescingFailureRecorder
