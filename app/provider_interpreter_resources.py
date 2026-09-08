# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide grouped dependencies for the interpreter."""

from typing import Annotated

from fastapi import Depends

from app import (
    loop_resources,
    provider_audit_storage as audit_providers,
    provider_control_support as support_providers,
    provider_fact_storage as fact_providers,
    provider_harness_registry as registry_providers,
    provider_harness_sessions as session_providers,
)

# Keep storage providers separate from runtime services.
# isort: split

from app import (
    provider_terminal as terminal_providers,
    provider_translation_inputs as input_providers,
    provider_translators as translator_providers,
)
from app.injection import singleton


@singleton
def interpreter_sources(
    session_storage: session_providers.Sessions,
    harnesses: registry_providers.Registry,
    raw: fact_providers.RawEvents,
    output: fact_providers.ShellOutput,
    events: fact_providers.CanonicalEvents,
) -> loop_resources.InterpreterSources:
    """Return source repositories for the interpreter.

    Returns:
        Source repositories for the interpreter.

    """
    return loop_resources.InterpreterSources(
        session_storage,
        harnesses,
        raw,
        output,
        events,
    )


InterpreterSourceSet = Annotated[
    loop_resources.InterpreterSources,
    Depends(interpreter_sources),
]


@singleton
def interpreter_services(
    translators: translator_providers.CoreTranslators,
    inputs: input_providers.TranslationInputs,
    audit: audit_providers.Recorder,
    interrupts: support_providers.InterruptTracking,
    adapter: terminal_providers.Terminal,
) -> loop_resources.InterpreterServices:
    """Return operational services for the interpreter.

    Returns:
        Operational services for the interpreter.

    """
    return loop_resources.InterpreterServices(
        translators,
        inputs,
        audit,
        interrupts,
        adapter,
    )


InterpreterServiceSet = Annotated[
    loop_resources.InterpreterServices,
    Depends(interpreter_services),
]
