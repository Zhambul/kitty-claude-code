# Copyright (c) 2026 Zhambyl Yermagambet
"""Create safe staged upload names."""

import pathlib
import re

ATTACHMENT_NAME_LIMIT = 80
UNSAFE_NAME_CHARACTERS = re.compile(r"[^A-Za-z0-9._-]")


def safe_attachment_name(name: str) -> str:
    """Return a safe basename for one staged attachment.

    Returns:
        The safe attachment name.

    """
    basename = pathlib.Path(name).name
    safe_name = UNSAFE_NAME_CHARACTERS.sub("_", basename).lstrip(".")
    return safe_name[:ATTACHMENT_NAME_LIMIT] or "attachment"
