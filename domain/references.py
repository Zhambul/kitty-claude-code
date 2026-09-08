# Copyright (c) 2026 Zhambyl Yermagambet
"""Stored references to harness models and user accounts."""

from dataclasses import dataclass

from domain.ids import AccountId
from domain.stored import STORED


@dataclass(frozen=True)
class ModelReference:
    """Hold a harness model identifier and its display name."""

    __pydantic_config__ = STORED

    name: str
    display_name: str | None


@dataclass(frozen=True)
class AccountReference:
    """Hold an account identifier and its display name."""

    __pydantic_config__ = STORED

    account_id: AccountId
    display_name: str
