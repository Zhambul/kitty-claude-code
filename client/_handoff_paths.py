# Copyright (c) 2026 Zhambyl Yermagambet
"""Build private temporary paths for pane handoff files."""

from __future__ import annotations

import os
import re
import tempfile
from pathlib import Path

PATH_COMPONENT_LIMIT = 120


class HandoffPaths:
    """Build paths for the private handoff files."""

    def pane_path(self, session_id: str, kind: str) -> str:
        """Return the pane document path.

        Returns:
            The pane document path.

        """
        return self._path("baqylau-pane-%d-%s-%s.json", session_id, kind)

    def view_path(self, session_id: str, kind: str) -> str:
        """Return the view document path.

        Returns:
            The view document path.

        """
        return self._path("baqylau-view-%d-%s-%s.json", session_id, kind)

    def lock_path(self, session_id: str, kind: str) -> str:
        """Return the pane lock path.

        Returns:
            The pane lock path.

        """
        return self._path("baqylau-pane-%d-%s-%s.lock", session_id, kind)

    def _path(self, template: str, session_id: str, kind: str) -> str:
        user_id = os.getuid()
        safe_session_id = self._safe(session_id)
        safe_kind = self._safe(kind)
        filename = template % (user_id, safe_session_id, safe_kind)
        return str(Path(tempfile.gettempdir()) / filename)

    def _safe(self, path_component: str) -> str:
        safe_component = re.sub(r"[^A-Za-z0-9_-]", "_", path_component)[:PATH_COMPONENT_LIMIT]
        return safe_component or "unnamed"


handoff_paths = HandoffPaths()
