# Copyright (c) 2026 Zhambyl Yermagambet
"""Store Claude session titles in transcripts."""

from pathlib import Path
from typing import override

from harness.impl.claude_code.canonical import records, transcript_paths
from harness.models import controls
from repository.contract.titles import NativeSessionTitleRepository

TEXT_ENCODING = "utf-8"


def set_session_title(path: str, name: str) -> bool | None:
    """Append a Claude naming record to a session transcript.

    Returns:
        True after the write, or None if this path does not support renaming.

    """
    if not transcript_paths.renameable(path):
        return None
    session_id = Path(path).stem
    record = records.TitleRecord(
        type="agent-name",
        agent_name=name,
        session_id=session_id,
    ).model_dump_json(exclude_none=True)
    with Path(path).open("a", encoding=TEXT_ENCODING) as sink:
        sink.write(f"{record}\n")
    return True


class TranscriptTitleRepository(NativeSessionTitleRepository):
    """Store native session titles in Claude transcripts."""

    @override
    def renameable(self, source_reference: str) -> bool:
        """Return whether the source can store a title.

        Returns:
            Whether the source can store a title.

        """
        return bool(transcript_paths.renameable(source_reference))

    def set_title(self, source_reference: str, title: str) -> controls.TitleWriteOutcome:
        """Set a native session title.

        Returns:
            Renamed after a successful write, unsupported for other paths, or unavailable on a write failure.

        """
        if not self.renameable(source_reference):
            return controls.TitleWriteOutcome.UNSUPPORTED
        try:
            written = set_session_title(source_reference, title)
        except OSError:
            return controls.TitleWriteOutcome.UNAVAILABLE
        if written:
            return controls.TitleWriteOutcome.RENAMED
        return controls.TitleWriteOutcome.UNAVAILABLE


titles = TranscriptTitleRepository()
