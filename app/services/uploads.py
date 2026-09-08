# Copyright (c) 2026 Zhambyl Yermagambet
"""Attachments the browser staged, and the prune that keeps them bounded.

The bytes are on disk because the harness is handed an `@path`; the row is what
makes them findable. This service owns the filesystem half — the repository
returns what it deleted and this unlinks it, because a repository does not
touch the filesystem.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import TYPE_CHECKING

from audit.documents import ShortErrorAudit

if TYPE_CHECKING:
    from collections.abc import Callable

    from audit.recorder import AuditRecorder
    from domain.uploads import StoredUpload
    from repository.contract.uploads import UploadRepository

# An attachment is delivered into a composer within minutes of being staged.
# A week is generous, and bounds a directory that previously grew forever.
UPLOAD_LIFETIME_SECONDS = 7 * 24 * 60 * 60


class UploadService:
    """Record staged uploads and remove expired upload files."""

    def __init__(
        self,
        upload_repository: UploadRepository,
        audit_recorder: AuditRecorder,
        clock: Callable[[], float] = time.time,
    ) -> None:
        """Create a service with upload storage and operational audit."""
        self.uploads = upload_repository
        self.audit = audit_recorder
        self.clock = clock

    def record(self, stored_upload: StoredUpload) -> None:
        """Record one staged upload."""
        self.uploads.record(stored_upload)

    def prune(self) -> int:
        """Remove expired upload rows and their files.

        Returns:
            Integer result.

        """
        removed = self.uploads.remove_expired(self.clock() - UPLOAD_LIFETIME_SECONDS)
        for stored_upload in removed:
            self._remove_file(stored_upload)
        return len(removed)

    def _remove_file(self, stored_upload: StoredUpload) -> None:
        try:
            Path(stored_upload.stored_path).unlink()
        except FileNotFoundError:
            return
        except OSError as error:
            self.audit.error(
                str(stored_upload.session_id or ""),
                "upload prune",
                ShortErrorAudit(error=f"{stored_upload.stored_path}: {error}"),
            )
