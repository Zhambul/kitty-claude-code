# Copyright (c) 2026 Zhambyl Yermagambet
"""Generate one normalized session title with a small model."""

from __future__ import annotations

from typing import TYPE_CHECKING

from inference.contract import ModelPromptRequest
from naming.titles import bounded_prompt, normalize_title

if TYPE_CHECKING:
    from inference.contract import ModelFactory

TITLE_PROMPT = """Create a short title for this coding session.

Return one plain-text title only.
Use 3 to 8 words.
Use at most 80 Unicode characters.
Do not use quotes, Markdown, paths, URLs, or terminal output.

User request:
{prompt}"""


class TitleGenerator:
    """Generate safe session titles with a small model."""

    def __init__(self, model_factory: ModelFactory) -> None:
        """Create a title generator with its model factory."""
        self.models = model_factory

    def generate(self, prompt: str, session_id: str) -> str:
        """Generate one normalized title from a bounded prompt.

        Returns:
            Text result.

        """
        bounded = bounded_prompt(prompt)
        request = ModelPromptRequest(
            TITLE_PROMPT.format(prompt=bounded),
            session_id,
        )
        response = self.models.small().send(request)
        return normalize_title(response.text)
