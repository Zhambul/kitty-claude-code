# Copyright (c) 2026 Zhambyl Yermagambet
"""Run one model provider in an isolated terminal tab."""

from __future__ import annotations

import tempfile
import time
from contextlib import ExitStack
from pathlib import Path
from typing import TYPE_CHECKING

from inference import commands, contract, errors, output, provider_errors
from terminal.models import tabs as tab_models, viewport as viewport_models

if TYPE_CHECKING:
    from inference.runner_resources import ModelRunnerResources
    from terminal.models.values import WindowId

PROVIDER_ATTEMPT_TIMEOUT_SECONDS = 30.0
POLL_SECONDS = 0.05


class ModelRunner:
    """Run one provider command and read its terminal output."""

    def __init__(
        self,
        resources: ModelRunnerResources,
    ) -> None:
        """Create a runner with terminal and runtime configuration."""
        self.terminal = resources.terminal_plugin
        self.runtime_configs = resources.runtime_configs
        self.timeout_seconds = resources.timeout_seconds

    def send(
        self,
        candidate: commands.ProviderCandidate,
        request: contract.ModelPromptRequest,
    ) -> contract.ModelPromptResponse:
        """Run one provider attempt and return its title.

        Returns:
            The model prompt response.

        """
        with ExitStack() as cleanup:
            directory = cleanup.enter_context(
                tempfile.TemporaryDirectory(prefix="baqylau-model-"),
            )
            schema_path = Path(directory) / "title-schema.json"
            schema_path.write_text(commands.TITLE_SCHEMA_JSON, encoding="utf-8")
            window_id = self._open(candidate, request, directory, schema_path)
            cleanup.callback(self._close, window_id)
            return self._read_response(window_id)

    def _open(
        self,
        candidate: commands.ProviderCandidate,
        request: contract.ModelPromptRequest,
        directory: str,
        schema_path: Path,
    ) -> WindowId:
        command = candidate.command(request.prompt, str(schema_path))
        runtime_config = self.runtime_configs.for_harness(candidate.harness)
        opened = self.terminal.tabs.open_tab(
            tab_models.TabOpenRequest(
                working_directory=directory,
                command=(candidate.executable, *command[1:]),
                title="Baqylau internal model",
                environment=commands.model_environment(candidate.harness, runtime_config),
            ),
        )
        if not opened.succeeded or opened.window_id is None:
            raise provider_errors.ProviderStartError(opened.reason)
        return opened.window_id

    def _read_response(self, window_id: WindowId) -> contract.ModelPromptResponse:
        self._wait_for_exit(window_id)
        time.sleep(POLL_SECONDS)
        screen = self.terminal.viewport.read_screen(
            viewport_models.ScreenReadRequest(window_id),
        )
        if not screen.succeeded or screen.text is None:
            raise provider_errors.ProviderOutputReadError(screen.reason)
        try:
            title = output.title_from_output(screen.text)
        except errors.ProviderUnavailableError as error:
            raise provider_errors.ProviderOutputParseError(error, screen.text) from error
        return contract.ModelPromptResponse(title)

    def _wait_for_exit(self, window_id: WindowId) -> None:
        deadline = time.monotonic() + min(
            self.timeout_seconds,
            PROVIDER_ATTEMPT_TIMEOUT_SECONDS,
        )
        while self._is_window_open(window_id):
            if time.monotonic() >= deadline:
                raise provider_errors.ProviderTimeoutError
            time.sleep(POLL_SECONDS)

    def _is_window_open(self, window_id: WindowId) -> bool:
        return any(window.window_id == window_id for window in self.terminal.metadata.windows())

    def _close(self, window_id: WindowId) -> None:
        self.terminal.tabs.close_tab(tab_models.TabCloseRequest(window_id))
