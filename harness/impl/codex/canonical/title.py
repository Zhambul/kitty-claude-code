# Copyright (c) 2026 Zhambyl Yermagambet
"""Codex native session-title repository."""

from __future__ import annotations

from pathlib import Path
from typing import override

from harness.impl.codex.canonical import rollout as rollout_records, title_paths, title_store, title_values
from harness.models.controls import TitleWriteOutcome
from repository.contract.titles import NativeSessionTitleRepository

CodexNativeTitle = title_values.CodexNativeTitle
CodexTitleStoreMarker = title_values.CodexTitleStoreMarker
title_store_marker = title_paths.title_store_marker


class CodexThreadTitleRepository(NativeSessionTitleRepository):
    """Read and write one Codex native thread title."""

    def __init__(self, configuration_directory: str) -> None:
        """Initialize the repository."""
        self.configuration_directory = configuration_directory

    @override
    def renameable(self, source_reference: str) -> bool:
        """Return whether this repository owns a rollout source.

        Returns:
            ``True`` if the rollout is owned by Codex.

        """
        return bool(rollout_records.owns(source_reference))

    def set_title(self, source_reference: str, title: str) -> TitleWriteOutcome:
        """Write the parked native title.

        Returns:
            The native title write outcome.

        """
        if not self.renameable(source_reference):
            return TitleWriteOutcome.UNSUPPORTED
        database = title_paths.state_database(source_reference, self.configuration_directory)
        thread_uuid = title_paths.thread_uuid(source_reference)
        if not database or not thread_uuid:
            return TitleWriteOutcome.UNAVAILABLE
        return title_store.set_title(database, thread_uuid, title)

    def read_title(self, source_reference: str) -> CodexNativeTitle | None:
        """Read the current native title.

        Returns:
            The native title, or ``None`` when unavailable.

        """
        if not self.renameable(source_reference):
            return None
        database = title_paths.state_database(source_reference, self.configuration_directory)
        thread_uuid = title_paths.thread_uuid(source_reference)
        if not database or not thread_uuid:
            return None
        return title_store.read_title(database, thread_uuid)


titles = CodexThreadTitleRepository(str(Path("~/.codex").expanduser()))
