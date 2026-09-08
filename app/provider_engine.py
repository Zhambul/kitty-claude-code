# Copyright (c) 2026 Zhambyl Yermagambet
"""Assemble the engine worker and its native input watches."""

from typing import Annotated

from fastapi import Depends

from app import provider_interpreter, provider_reaction_loop, provider_runtime
from app.injection import singleton
from app.provider_work_queue import EngineWork
from engine.interpret.loop import Interpreter
from engine.react.loop import ReactionLoop
from engine.worker import EngineWorker


@singleton
def engine_worker(
    interpreter: Annotated[Interpreter, Depends(provider_interpreter.interpreter)],
    reaction_loop: Annotated[ReactionLoop, Depends(provider_reaction_loop.reaction_loop)],
    work_queue: EngineWork,
    runtime_configs: provider_runtime.RuntimeConfigs,
) -> EngineWorker:
    """Build the event-driven engine worker.

    Returns:
        The shared engine worker.

    """
    return EngineWorker(
        interpreter,
        reaction_loop,
        work_queue,
        tuple(entry.config.configuration_directory for entry in runtime_configs.entries()),
    )
