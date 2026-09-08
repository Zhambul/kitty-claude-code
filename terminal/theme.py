# Copyright (c) 2026 Zhambyl Yermagambet
"""Canonical actor statuses mapped to the established terminal color palette."""

from types import MappingProxyType

from domain.actor_state import ActorStatus
from terminal.models.values import RGB, TabAppearance

LIGHT_TEXT = RGB.from_hex("#e6e9ef")
INACTIVE_TEXT = RGB.from_hex("#c0c4cc")

TAB_APPEARANCES = MappingProxyType({
    ActorStatus.IDLE: TabAppearance(RGB.from_hex("#5c6370"), LIGHT_TEXT, RGB.from_hex("#33373f"), INACTIVE_TEXT),
    ActorStatus.THINKING: TabAppearance(
        RGB.from_hex("#c678dd"),
        RGB.from_hex("#1a0620"),
        RGB.from_hex("#4a2b52"),
        INACTIVE_TEXT,
    ),
    ActorStatus.WORKING: TabAppearance(
        RGB.from_hex("#c678dd"),
        RGB.from_hex("#1a0620"),
        RGB.from_hex("#4a2b52"),
        INACTIVE_TEXT,
    ),
    ActorStatus.EXECUTING: TabAppearance(
        RGB.from_hex("#61afef"),
        RGB.from_hex("#06121f"),
        RGB.from_hex("#2c4a63"),
        INACTIVE_TEXT,
    ),
    ActorStatus.AWAITING_BACKGROUND: TabAppearance(
        RGB.from_hex("#61afef"),
        RGB.from_hex("#06121f"),
        RGB.from_hex("#2c4a63"),
        INACTIVE_TEXT,
    ),
    ActorStatus.AWAITING_ATTENTION: TabAppearance(
        RGB.from_hex("#e06c75"),
        RGB.from_hex("#2a0608"),
        RGB.from_hex("#5e2d31"),
        INACTIVE_TEXT,
    ),
    ActorStatus.AWAITING_RESPONSE: TabAppearance(
        RGB.from_hex("#98c379"),
        RGB.from_hex("#07180a"),
        RGB.from_hex("#445733"),
        INACTIVE_TEXT,
    ),
})


def tab_appearance(actor_status: ActorStatus) -> TabAppearance:
    """Return the tab appearance.

    Returns:
        Tab appearance.

    """
    return TAB_APPEARANCES[actor_status]
