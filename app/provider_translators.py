# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide translators for application-owned raw event sources."""

from collections.abc import Mapping
from typing import Annotated

from fastapi import Depends

from app.injection import singleton
from engine.interpret import translators as interpreter_translators
from harness import contract
from harness.models.raw_events import (
    AUTOMATIC_TITLE_SOURCE_TYPE,
    CONTROL_SOURCE_TYPE,
    INTERRUPT_SOURCE_TYPE,
    LIVENESS_SOURCE_TYPE,
    OUTPUT_LOCATION_SOURCE_TYPE,
    RESUME_LIVENESS_SOURCE_TYPE,
    RESUME_SOURCE_TYPE,
)


@singleton
def core_translators() -> Mapping[str, contract.CoreTranslator]:
    """Return translators for application-owned raw event sources.

    Returns:
        Translators for application-owned raw event sources.

    """
    return {
        AUTOMATIC_TITLE_SOURCE_TYPE: interpreter_translators.AutomaticTitleTranslator(),
        CONTROL_SOURCE_TYPE: interpreter_translators.ControlTranslator(),
        OUTPUT_LOCATION_SOURCE_TYPE: interpreter_translators.ShellOutputTranslator(),
        LIVENESS_SOURCE_TYPE: interpreter_translators.LivenessTranslator(),
        RESUME_SOURCE_TYPE: interpreter_translators.SessionResumeTranslator(),
        RESUME_LIVENESS_SOURCE_TYPE: interpreter_translators.ResumeLivenessTranslator(),
        INTERRUPT_SOURCE_TYPE: interpreter_translators.InterruptTranslator(),
    }


CoreTranslators = Annotated[
    Mapping[str, contract.CoreTranslator],
    Depends(core_translators),
]
