# Copyright (c) 2026 Zhambyl Yermagambet
"""Cross-harness canonical translation tests from native fixture shapes."""

from __future__ import annotations

from collections.abc import Callable

from terminal.models import input as terminal_input

type TextSubmitCallback = Callable[
    [terminal_input.TextSubmitRequest],
    terminal_input.TextSubmitResponse,
]


type TextInsertCallback = Callable[
    [terminal_input.TextInsertRequest],
    terminal_input.TextInsertResponse,
]


type KeySendCallback = Callable[
    [terminal_input.KeySendRequest],
    terminal_input.KeySendResponse,
]
