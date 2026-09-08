# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the account reference module."""

# Which account a session is billed to.
from pydantic import BaseModel


class AccountReferenceResponse(BaseModel):
    """Represent account reference response."""

    account_id: str
    display_name: str
