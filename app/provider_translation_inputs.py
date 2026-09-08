# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide reactions required before the next interpretation pull."""

from typing import Annotated

from fastapi import Depends

from app import (
    provider_fact_storage as fact_providers,
    provider_harness_sessions as session_providers,
    provider_runtime as runtime_providers,
)
from app.injection import singleton
from engine.interpret import reactions
from harness import contract


@singleton
def translation_inputs(
    session_storage: session_providers.Sessions,
    output: fact_providers.ShellOutput,
    raw: fact_providers.RawEvents,
    repositories: runtime_providers.Repositories,
) -> tuple[contract.CanonicalEventReaction, ...]:
    """Return reactions required before the next source pull.

    Returns:
        Reactions required before the next source pull.

    """
    return (
        reactions.SessionUpsertCanonicalEventReaction(
            session_storage,
            repositories,
        ),
        reactions.ShellOutputCanonicalEventReaction(output, raw),
    )


TranslationInputs = Annotated[
    tuple[contract.CanonicalEventReaction, ...],
    Depends(translation_inputs),
]
