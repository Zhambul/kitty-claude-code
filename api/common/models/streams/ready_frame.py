# Copyright (c) 2026 Zhambyl Yermagambet
"""The server identity sent when the global event stream opens."""

from pydantic import BaseModel


class ReadyFrame(BaseModel):
    """Represent ready frame."""

    boot_id: str
