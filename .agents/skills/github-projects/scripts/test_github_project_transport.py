# Copyright (c) 2026 Zhambyl Yermagambet
"""Check GitHub transport boundaries without network or credential access."""

from http import HTTPStatus
from unittest.mock import MagicMock, Mock

import github_project_transport as transport
import pytest
from github_project_errors import GitHubProjectError


@pytest.fixture
def token_command(monkeypatch: pytest.MonkeyPatch) -> Mock:
    """Replace the GitHub token command and hide inherited token variables.

    Returns:
        The token command probe with a test-only token.

    """
    command = Mock(return_value=Mock(stdout="test-token\n"))
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("GH_TOKEN", raising=False)
    monkeypatch.setattr("github_project_transport.shutil.which", lambda _name: "/test/gh")
    monkeypatch.setattr("github_project_transport.subprocess.run", command)
    return command


@pytest.mark.parametrize("api_address", ["http://api.invalid", "file:///tmp/api", "ftp://api.invalid"])
def test_transport_rejects_non_https(api_address: str) -> None:
    """Reject non-HTTPS API addresses before a request can be built."""
    with pytest.raises(GitHubProjectError, match="API address must use https"):
        transport.HttpTransport("test-token", api_address)


def test_transport_sends_https(monkeypatch: pytest.MonkeyPatch) -> None:
    """Build an HTTPS request with the supplied test token."""
    response = MagicMock()
    response.__enter__.return_value.status = HTTPStatus.NO_CONTENT
    network = Mock(return_value=response)
    monkeypatch.setattr(transport, "urlopen", network)
    client = transport.HttpTransport("test-token", "https://api.invalid")
    assert client.request("GET", "/test") == {}
    network.assert_called_once()
    request = network.call_args.args[0]
    assert request.full_url == "https://api.invalid/test"
    assert request.get_header("Authorization") == "Bearer test-token"


def test_token_command_uses_resolved_path(token_command: Mock) -> None:
    """Use the resolved GitHub CLI with fixed authentication arguments."""
    assert isinstance(transport.HttpTransport.from_environment(), transport.HttpTransport)
    token_command.assert_called_once_with(
        ["/test/gh", "auth", "token"], check=True, capture_output=True, text=True, timeout=10,
    )


def test_missing_cli_does_not_start_process(monkeypatch: pytest.MonkeyPatch, token_command: Mock) -> None:
    """Report a missing GitHub CLI without starting a process."""
    monkeypatch.setattr("github_project_transport.shutil.which", lambda _name: None)
    with pytest.raises(GitHubProjectError, match="Set GITHUB_TOKEN or authenticate with gh"):
        transport.HttpTransport.from_environment()
    token_command.assert_not_called()
