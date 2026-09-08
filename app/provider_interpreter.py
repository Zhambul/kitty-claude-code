# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the canonical event interpreter."""

from app import provider_harness_launch as launch_providers, provider_interpreter_resources as resource_providers
from app.injection import singleton
from engine.interpret import dependencies, loop


@singleton
def interpreter(
    sources: resource_providers.InterpreterSourceSet,
    services: resource_providers.InterpreterServiceSet,
    effects: launch_providers.LaunchEffects,
) -> loop.Interpreter:
    """Return the canonical event interpreter.

    Returns:
        Canonical event interpreter.

    """
    return loop.Interpreter(
        dependencies.InterpreterDependencies(
            repositories=dependencies.InterpreterRepositories(
                sessions=sources.session_repository,
                raw_events=sources.raw_event_repository,
                shell_output=sources.shell_output_repository,
                canonical_events=sources.canonical_event_repository,
            ),
            services=dependencies.InterpreterServices(
                harnesses=sources.harness_registry,
                core_translators=services.translators,
                inputs=services.input_reactions,
                audit=services.audit_recorder,
                interrupts=services.interrupt_registry,
            ),
            runtime=dependencies.InterpreterRuntime(
                terminal=services.terminal_adapter,
                resume_recorder=effects,
            ),
        ),
    )
