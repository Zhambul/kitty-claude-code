# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide http test audit models."""

from __future__ import annotations

from tests import (
    http_application_dependencies as application_dependencies,
    http_contract_dependencies as contract_dependencies,
    http_library_dependencies as library_dependencies,
    http_runtime_dependencies as runtime_dependencies,
    http_value_dependencies as standard_dependencies,
)

type ControlAuditRow = tuple[str, str, contract_dependencies.control_services.ControlAudit]
type MethodAuditRow = tuple[str, contract_dependencies.control_services.ControlAudit]


@standard_dependencies.dataclasses.dataclass(frozen=True)
class PresenceCall:
    """Record one presence action with its device and session."""

    action: str
    device: str | None = None
    session_id: runtime_dependencies.domain_ids.SessionId | None = None


@standard_dependencies.dataclasses.dataclass(frozen=True)
class AssetReference:
    """Keep an asset URL, file suffix, and optional build-relative path."""

    path: str
    suffix: str
    build_path: str | None

    @classmethod
    def from_bytes(cls, reference: bytes) -> AssetReference:
        """Parse an encoded asset reference.

        Returns:
            The asset path and file details used by response checks.

        """
        path = reference.decode()
        name = path.split("?")[0].rsplit("/", 1)[1]
        extension = name.rsplit(".", 1)[1]
        build_path = path.removeprefix("/static/build/") if path.startswith("/static/build/") else None
        return cls(path, f".{extension}", build_path)


class BrowserAudit:
    """Record browser state files without writing audit data."""

    def __init__(self) -> None:
        """Create an empty state file record."""
        self.records: list[tuple[runtime_dependencies.domain_ids.SessionId, str, str, str]] = []

    def record_state_file(self, state_file: application_dependencies.StateFileRecord) -> None:
        """Record the session, path, action, and state file content."""
        self.records.append((state_file.session_id, state_file.path, state_file.action, state_file.content))


class ControlAuditRecorder(application_dependencies.AuditRecorder):
    """Record control audit content in a shared test list."""

    def __init__(self, rows: list[ControlAuditRow]) -> None:
        """Store the shared control audit list."""
        self._rows = rows

    def state_file(self, log: str, path: str, action: str, content: application_dependencies.AuditContent = "") -> None:
        """Record a control audit row and its last path."""
        self.last_path = path
        assert isinstance(content, contract_dependencies.control_services.ControlAudit)
        self._rows.append((log, action, content))


class BrokenControlAudit(application_dependencies.AuditRecorder):
    """Simulate a locked audit database."""

    def __init__(self) -> None:
        """Start without a failed write record."""
        self.failed_write: tuple[str, str, str, application_dependencies.AuditContent] | None = None

    def state_file(
        self, log: str, path: str, action: str, content: application_dependencies.AuditContent = "",
    ) -> library_dependencies.typing.Never:
        """Record a write attempt and simulate its failure.

        Raises:
            OperationalError: For every write attempt.

        """
        self.failed_write = (log, path, action, content)
        message = "database is locked"
        raise standard_dependencies.sqlite3.OperationalError(message)


class MissingSessions:
    """Record session lookups and report no matching session."""

    def find(self, session_id: runtime_dependencies.domain_ids.SessionId) -> contract_dependencies.Session | None:
        """Record the requested session identifier.

        Returns:
            None for every lookup.

        """
        self.last_session_id = session_id
        missing_session: contract_dependencies.Session | None = None
        return missing_session


class MethodAuditRecorder(application_dependencies.AuditRecorder):
    """Record control method audit actions and their content."""

    def __init__(self, rows: list[MethodAuditRow]) -> None:
        """Store the shared method audit list."""
        self._rows = rows

    def state_file(self, log: str, path: str, action: str, content: application_dependencies.AuditContent = "") -> None:
        """Record the action, control content, and last log location."""
        self.last_location = (log, path)
        assert isinstance(content, contract_dependencies.control_services.ControlAudit)
        self._rows.append((action, content))
