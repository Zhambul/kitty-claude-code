# Copyright (c) 2026 Zhambyl Yermagambet
"""Contain services that bind one named reference from another."""

from __future__ import annotations

from dataclasses import dataclass

from sdk.client import BaqylauClient
from tests.e2e.testkit.policy import WaitPolicy
from tests.e2e.testkit.references import References


@dataclass(frozen=True)
class ReferenceBindingContext[SourceReferenceT, TargetReferenceT]:
    """Contain services that bind target references from source references."""

    client: BaqylauClient
    sources: References[SourceReferenceT]
    targets: References[TargetReferenceT]
    wait_policy: WaitPolicy
