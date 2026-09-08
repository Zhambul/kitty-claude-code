# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the middleware module."""

# api/middleware.py — what wraps EVERY response, in one place.
#
# Two policies, both about the response and neither about any route: the
# security headers every reply carries, and the compression exemption the event
# streams need. They are ASGI middleware rather than route dependencies because
# a route is exactly the thing they must not have to know about — including the
# static server, the two raw-event-plane endpoints that answer in a harness's own
# bytes, and the error handlers.
from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING

from starlette.datastructures import MutableHeaders
from starlette.middleware.gzip import GZipMiddleware

if TYPE_CHECKING:
    from collections.abc import Mapping

    from starlette.types import ASGIApp, Message, Receive, Scope, Send


async def _send_with_headers(
    message: Message,
    *,
    headers: Mapping[str, str],
    send: Send,
) -> None:
    if message["type"] == "http.response.start":
        response_headers = MutableHeaders(scope=message)
        for name, header_content in headers.items():
            if name not in response_headers:
                response_headers[name] = header_content
    await send(message)


class SecurityHeaders:
    """Stamp the policy's security headers onto every response.

    The headers arrive by CONSTRUCTOR, not by import: ASGI middleware runs
    outside the dependency graph — there is no request to resolve against yet —
    so `add_middleware` is where this layer gets injected.

    Applied here, as the outermost thing `add_middleware` can install, so it
    reaches the replies no handler produced — a guard's 403, the framework's 404
    — and the streaming ones, whose headers go out long before their body ends.
    The single response it cannot wrap is the 500 from Starlette's own
    ServerErrorMiddleware, which sits above every user middleware; api/app.py
    `_error_body` stamps that one from the same constant.

    Only ever ADDS: a route that set a header itself (the static server's
    Cache-Control) keeps its value, because a policy that silently overwrote a
    handler's own decision would be a second, invisible owner of it.
    """

    def __init__(self, app: ASGIApp, headers: Mapping[str, str]) -> None:
        """Initialize the object."""
        self.app = app
        self.headers = headers

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Call the object."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        await self.app(
            scope,
            receive,
            partial(_send_with_headers, headers=self.headers, send=send),
        )


class SelectiveGZip:
    """Represent selective gzip.

    Gzip everything except the event streams: compressing SSE would buffer
        the incremental frames the streams exist to deliver. An EventSource always
        sends `Accept: text/event-stream`, which is the routing fact used here.
    """

    def __init__(self, app: ASGIApp, minimum_size: int) -> None:
        """Initialize the object."""
        self.plain = app
        self.compressing = GZipMiddleware(app, minimum_size=minimum_size)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Call the object."""
        if scope["type"] == "http":
            headers = dict(scope.get("headers") or ())
            if b"text/event-stream" in headers.get(b"accept", b""):
                await self.plain(scope, receive, send)
                return
        await self.compressing(scope, receive, send)
