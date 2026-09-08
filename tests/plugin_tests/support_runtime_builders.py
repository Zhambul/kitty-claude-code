# Copyright (c) 2026 Zhambyl Yermagambet
"""Build plugin test runtime dependencies."""

from types import SimpleNamespace

from engine.interpret import (
    loop as interpret_loop,
    reactions as interpret_reactions,
    translators as interpret_translators,
)
from engine.interpret.loop import Interpreter
from harness.impl.discovery import installed
from harness.models import raw_events as raw_event_models
from harness.models.interrupts import InterruptRegistry
from harness.registry import HarnessRegistry
from tests.canonical_runtime import CanonicalRuntime
from tests.fake_terminal import FakeTerminal
from tests.plugin_tests.support_audit import silent_audit


def harness_registry() -> HarnessRegistry:
    """Create a registry with the installed harness plugins.

    Returns:
        A registry with the installed harness plugins.

    """
    registry = HarnessRegistry()
    terminal = FakeTerminal()
    for plugin in installed(
        terminal_plugin=terminal.plugin(),
        session_resume_recorder=SimpleNamespace(
            resumed=lambda *_arguments: None,
        ),
        audit_recorder=silent_audit(),
    ):
        registry.register(plugin)
    registry.validate()
    return registry


def interpreter(
    runtime: CanonicalRuntime,
    registry: HarnessRegistry,
) -> Interpreter:
    """Create an interpreter for one test runtime.

    Returns:
        An interpreter for one test runtime.

    """
    return Interpreter(
        interpret_loop.InterpreterDependencies(
            repositories=interpret_loop.InterpreterRepositories(
                sessions=runtime.sessions,
                raw_events=runtime.recorder,
                shell_output=runtime.shell_output,
                canonical_events=runtime.store,
            ),
            services=interpret_loop.InterpreterServices(
                harnesses=registry,
                core_translators={
                    raw_event_models.OUTPUT_LOCATION_SOURCE_TYPE: interpret_translators.ShellOutputTranslator(),
                    raw_event_models.LIVENESS_SOURCE_TYPE: interpret_translators.LivenessTranslator(),
                },
                inputs=(
                    interpret_reactions.SessionUpsertCanonicalEventReaction(runtime.sessions),
                    interpret_reactions.ShellOutputCanonicalEventReaction(
                        runtime.shell_output,
                        runtime.recorder,
                    ),
                ),
                audit=silent_audit(),
                interrupts=InterruptRegistry(),
            ),
        ),
    )
