# Copyright (c) 2026 Zhambyl Yermagambet
"""Domain and harness value objects to the api's own.

Pure functions: no I/O, no service, no request. `maybe_*` is the nullable form,
because `x if x is None else f(x)` at eleven call sites is eleven chances to
get the polarity backwards.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from api.common.models.values.account_reference import AccountReferenceResponse
from api.common.models.values.content import ContentResponse
from api.common.models.values.model_reference import ModelReferenceResponse
from api.common.models.values.plan_choice import PlanChoiceResponse
from domain.content import Content, MediaType, StructuredContent, content_text

if TYPE_CHECKING:
    from domain.references import AccountReference, ModelReference
    from harness.models.controls import (
        PlanChoice,
    )


def model_reference(model_reference: ModelReference) -> ModelReferenceResponse:
    """Return the model reference.

    Returns:
        Model reference.

    """
    return ModelReferenceResponse(
        name=model_reference.name,
        display_name=model_reference.display_name,
    )


def maybe_model_reference(
    candidate_model_reference: ModelReference | None,
) -> ModelReferenceResponse | None:
    """Return the model reference, if it exists.

    Returns:
        Model reference, if it exists.

    """
    return None if candidate_model_reference is None else model_reference(candidate_model_reference)


def maybe_account_reference(
    account_reference: AccountReference | None,
) -> AccountReferenceResponse | None:
    """Return the account reference, if it exists.

    Returns:
        Account reference, if it exists.

    """
    if account_reference is None:
        return None
    return AccountReferenceResponse(
        account_id=account_reference.account_id,
        display_name=account_reference.display_name,
    )


def content(document_content: Content) -> ContentResponse:
    """Return the content.

    Text and how to draw it. A structured document — a tool's own arguments
        or answer, in a shape we do not define — is laid out as the plain text a
        person reads, which is the only thing a client can do with it.

    Returns:
        Content.

    """
    if isinstance(document_content, StructuredContent):
        return ContentResponse(text=content_text(document_content), media_type=MediaType.TEXT_PLAIN)
    return ContentResponse(text=document_content.text, media_type=document_content.media_type)


def maybe_content(document_content: Content | None) -> ContentResponse | None:
    """Return the content, if it exists.

    Returns:
        Content, if it exists.

    """
    return None if document_content is None else content(document_content)


def plan_choice(plan_choice: PlanChoice) -> PlanChoiceResponse:
    """Return the plan choice.

    Returns:
        Plan choice.

    """
    return PlanChoiceResponse(
        digit=plan_choice.digit,
        label=plan_choice.label,
        feedback=plan_choice.feedback,
    )
