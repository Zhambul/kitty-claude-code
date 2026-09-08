# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide browser client dependencies."""

from typing import Protocol as Protocol
from urllib.parse import quote as quote, urlsplit as urlsplit

from playwright.sync_api import (
    ConsoleMessage as ConsoleMessage,
    Locator as Locator,
    Page as Page,
    Request as Request,
    Route as Route,
)
