# Copyright (c) 2026 Zhambyl Yermagambet
"""Shared fixtures and builders for canonical harness tests."""

from __future__ import annotations

from typing import TYPE_CHECKING

from domain import content as domain_content

if TYPE_CHECKING:
    from harness import contract as harness_contract

type JsonValue = bool | float | int | str | list[JsonValue] | dict[str, JsonValue] | None


def text_of(content: domain_content.Content | None) -> str:
    """Return the text content that a text event must carry.

    Returns:
        The text content that a text event must carry.

    """
    assert isinstance(content, domain_content.TextContent)
    return content.text


def structured_of(content: domain_content.Content | None) -> domain_content.StructuredContent:
    """Return the structured content that a structured event must carry.

    Returns:
        The structured content that a structured event must carry.

    """
    assert isinstance(content, domain_content.StructuredContent)
    return content


def controller_of(plugin: harness_contract.HarnessPlugin) -> harness_contract.HarnessController:
    """Return the controller that a controllable harness must provide.

    Returns:
        The controller that a controllable harness must provide.

    """
    assert plugin.controller is not None
    return plugin.controller


def json_object(document: dict[str, JsonValue]) -> dict[str, JsonValue]:
    """Keep a nested test document inside the JSON value contract.

    Returns:
        The supplied document without changes.

    """
    return document
