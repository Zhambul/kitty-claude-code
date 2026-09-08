# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the process-local engine work notices."""

from typing import Annotated

from fastapi import Depends

from app.injection import singleton
from core.work_queue import WorkQueue


@singleton
def work_queue() -> WorkQueue:
    """Build the engine work queue.

    Returns:
        The shared work queue.

    """
    return WorkQueue()


EngineWork = Annotated[WorkQueue, Depends(work_queue)]
