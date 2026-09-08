# Copyright (c) 2026 Zhambyl Yermagambet
"""Declare audit documents for inference provider state."""

from decimal import Decimal
from typing import Literal

from audit.documents import AuditDocument
from domain.ids import HarnessName


class ExecutableUnavailable(AuditDocument):
    """Describe a provider whose executable is not available."""

    provider: HarnessName
    status: Literal["executable unavailable"]
    configuration: str


class CapacityUnavailable(AuditDocument):
    """Describe a provider that has no remaining capacity."""

    provider: HarnessName
    status: Literal["capacity unavailable"]
    remaining_capacity_percent: Decimal


class AvailableProvider(AuditDocument):
    """Describe a provider that can accept model work."""

    provider: HarnessName
    status: Literal["available"]
    remaining_capacity_percent: Decimal


type ProviderState = ExecutableUnavailable | CapacityUnavailable | AvailableProvider
