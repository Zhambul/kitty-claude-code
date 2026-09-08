# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide sqlite library dependencies."""

from domain import (
    content as _domain_content,
    dialogs as dialogs,
    entries as _domain_entries,
    entry_conversation as entry_conversation,
    entry_shells as entry_shells,
)

# Keep canonical events separate from read-model entries.
# isort: split

from domain import (
    event_base as event_base,
    event_conversation as event_conversation,
    event_resource as event_resource,
    event_session as event_session,
    event_shell as event_shell,
)

domain_content = _domain_content
domain_entries = _domain_entries
