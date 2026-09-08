# Copyright (c) 2026 Zhambyl Yermagambet
"""Own Web Push payloads."""

from __future__ import annotations

import dataclasses
from typing import Literal

from pydantic import BaseModel, ConfigDict

from domain.ids import SessionId
from notify.presence import RoutedSubscription

EMPTY_SESSION_ID = SessionId("")


class WebPushAlertPayload(BaseModel):
    """Represent web push alert payload.

    The push body for a fresh alert — `static/sw.js` shows it verbatim
        (title/body/badge), and reads `session_id`/`kind` back into its own
        click-through and the resolve push's tag.
    """

    model_config = ConfigDict(frozen=True)

    title: str
    body: str
    session_id: SessionId
    kind: str | None
    url: str
    badge: int


@dataclasses.dataclass(frozen=True)
class _WebPushAlertFields:
    title: str
    body: str
    session_id: SessionId
    kind: str | None
    url: str
    badge: int


class WebPushResolvePayload(BaseModel):
    """Represent web push resolve payload.

    The push body that closes a delivered alert — `type` is what
        `static/sw.js` branches on to resolve rather than show a notification.
    """

    model_config = ConfigDict(frozen=True)

    session_id: SessionId
    kind: str | None
    tag: str
    badge: int
    type: Literal["resolve"] = "resolve"


WebPushPayload = WebPushAlertPayload | WebPushResolvePayload


@dataclasses.dataclass
class WebPushHandle:
    """Represent web push handle.

    The retraction handle `send_alert` hands back: the subscriptions the
        alert actually went to (a resolve push must reach those, never whichever
        device is most-recently-used by the time it fires) and the tag they were
        shown under.
    """

    ch: Literal["webpush"] = "webpush"
    session_id: SessionId = EMPTY_SESSION_ID
    kind: str | None = None
    subs: list[RoutedSubscription] = dataclasses.field(default_factory=list)
    tag: str = ""
