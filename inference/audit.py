# Copyright (c) 2026 Zhambyl Yermagambet
"""Declare audit documents for inference failures."""

from audit.documents import AuditDocument
from domain.ids import HarnessName
from inference.provider_state import ProviderState


class InferenceErrorAudit(AuditDocument):
    """Describe one inference exception."""

    error_type: str
    error: str


class ProviderAttemptAudit(InferenceErrorAudit):
    """Describe an unexpected provider-attempt exception."""

    provider: HarnessName
    attempt: int


class ModelUnavailableAudit(InferenceErrorAudit):
    """Describe the final state of all unavailable providers."""

    providers: tuple[ProviderState, ...]
    attempt_failures: tuple[str, ...]


def error_context(error: Exception) -> InferenceErrorAudit:
    """Convert an exception to a small audit document.

    Returns:
        The inference error audit.

    """
    return InferenceErrorAudit(error_type=type(error).__name__, error=str(error))
