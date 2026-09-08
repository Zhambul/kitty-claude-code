# Copyright (c) 2026 Zhambyl Yermagambet
"""Create automatic naming jobs from semantic user prompts."""

from __future__ import annotations

from typing import TYPE_CHECKING

from domain.content import TextContent
from domain.event_conversation import MessageCreated
from domain.naming import NamingJob
from naming.titles import bounded_prompt

if TYPE_CHECKING:
    from domain.event_base import CanonicalEvent, EventPayload
    from harness.registry import HarnessRegistry
    from repository.contract.naming import NamingJobRepository


class AutomaticNamingReaction:
    """Enqueue the first user prompt when a harness needs generic naming."""

    def __init__(
        self,
        harness_registry: HarnessRegistry,
        naming_job_repository: NamingJobRepository,
    ) -> None:
        """Create a reaction with harness and job repositories."""
        self.registry = harness_registry
        self.jobs = naming_job_repository

    def react(self, event: CanonicalEvent[EventPayload]) -> None:
        """Enqueue a valid first prompt for generic naming."""
        payload = event.payload
        prompt_content = _user_prompt_content(payload)
        if prompt_content is None:
            return
        if self.registry.plugin(event.harness).harness_info.supports_native_initial_naming:
            return
        prompt = bounded_prompt(prompt_content.text)
        if prompt:
            self.jobs.enqueue(
                NamingJob(f"initial:{event.session_id}", event.session_id, prompt),
            )


def _user_prompt_content(payload: EventPayload) -> TextContent | None:
    if not isinstance(payload, MessageCreated):
        return None
    if payload.role != "user" or payload.phase != "prompt":
        return None
    return payload.content if isinstance(payload.content, TextContent) else None
