# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide shared services for harness controls."""

from typing import Annotated

from fastapi import Depends

from app import (
    provider_fact_storage as fact_providers,
    provider_harness_registry as registry_providers,
    provider_harness_sessions as session_providers,
    provider_runtime as runtime_providers,
    provider_session_storage as session_data_providers,
    provider_terminal as terminal_providers,
)
from app.injection import singleton
from app.provider_work_queue import EngineWork
from core.work_queue import WorkKind
from engine.interpret.interrupts import GRACE_SECONDS
from harness.models.interrupts import InterruptRegistry
from harness.services import catalog as catalog_contract, control_effects, probe, terminal_gate


@singleton
def interrupt_registry(work_queue: EngineWork) -> InterruptRegistry:
    """Return the in-memory interrupt registry.

    Returns:
        In-memory interrupt registry.

    """
    return InterruptRegistry(
        lambda marked_at: work_queue.schedule(
            WorkKind.SOURCES,
            GRACE_SECONDS,
            key=f"interrupt:{marked_at}",
        ),
    )


InterruptTracking = Annotated[
    InterruptRegistry,
    Depends(interrupt_registry),
]


@singleton
def control_effects_service(
    raw: fact_providers.RawEvents,
    read_model: session_data_providers.SessionDataStore,
) -> control_effects.ControlEffectRecorder:
    """Return the durable control effect recorder.

    Returns:
        Durable control effect recorder.

    """
    return control_effects.ControlEffectRecorder(raw, read_model)


ControlEffects = Annotated[
    control_effects.ControlEffectRecorder,
    Depends(control_effects_service),
]


@singleton
def catalog(
    harnesses: registry_providers.Registry,
) -> catalog_contract.HarnessCatalogService:
    """Return the harness catalog service.

    Returns:
        Harness catalog service.

    """
    return catalog_contract.HarnessCatalogService(harnesses)


Catalog = Annotated[catalog_contract.HarnessCatalogService, Depends(catalog)]


@singleton
def terminal_input(
    session_storage: session_providers.Sessions,
    adapter: terminal_providers.Terminal,
    plugin: runtime_providers.InstalledTerminal,
) -> probe.TerminalInputService:
    """Return the terminal input probe service.

    Returns:
        Terminal input probe service.

    """
    return probe.TerminalInputService(session_storage, adapter, plugin)


TerminalInput = Annotated[probe.TerminalInputService, Depends(terminal_input)]


@singleton
def session_terminal_gate() -> terminal_gate.SessionTerminalGate:
    """Return the per-session terminal control gate.

    Returns:
        Per-session terminal control gate.

    """
    return terminal_gate.SessionTerminalGate()


TerminalGate = Annotated[
    terminal_gate.SessionTerminalGate,
    Depends(session_terminal_gate),
]
