# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the alert module."""

# notify/channels/alert.py — what an alert SAYS, and how a send can end.
#
# The two pieces both channels share. `alert_text` builds the same three
# strings from one entry (each channel composes them differently); `push_tag`
# is the one encoding of the notification tag, which the sender, the retraction
# and the service worker (static/sw.js) must all agree on.
#
# The outcome vocabulary lives here rather than in the package __init__ so a
# channel can name it without importing the dispatcher that imports the
# channel.
from dataclasses import dataclass
from urllib.parse import quote

from dashboard import config
from domain.ids import SessionId

# `retract()` outcome vocabulary. Everything except PENDING is settled — the
# caller forgets the record. PENDING means the SEND is still in flight (the
# Telegram round-trip runs on its own thread, so a retraction can genuinely
# arrive first): keep the record and ask again on the next tick.
PENDING = "pending"  # send not landed yet — retry next tick
OK = "ok"  # retracted
GONE = "gone"  # already gone from the chat — the same thing, cheaper
FAILED = "failed"  # the service said no; the alert is still out there
NOTHING = "nothing"  # the send never landed anything — nothing to take back


@dataclass(frozen=True)
class Alert:
    """Represent alert."""

    session_id: SessionId
    state: str
    kind: str
    project: str
    title: str


def alert_text(alert: Alert) -> tuple[str, str, str]:
    """Return the alert text.

    The alert pieces both channels build the same way from one `entry`: the
        🔴/🟢 headline (project + needs-you/is-done), the detail line (the session
        title, or a kind-specific fallback), and the ?s=<session_id> deep link. Returns the
        three RAW strings only — each channel composes them differently (Telegram
        joins them into one message; Web Push splits them across the payload's
        title/body), so the joining/escaping stays at the call site.

        ?s=<session_id>, NOT the app's #/s/<session_id> hash route: Telegram's auto-linker drops
        the URL fragment, so a #-link opens the dashboard ROOT on the phone, not the
        session. The session_id rides a query param (linkified whole); the page translates
        ?s=<session_id> back into the hash route on load.

    Returns:
        Alert text.

    """
    project_name = alert.project or alert.session_id or "session"
    headline = f"🟢 {project_name} is done"
    fallback_detail = "finished — your turn"
    if alert.kind == "asking":
        headline = f"🔴 {project_name} needs you"
        fallback_detail = "a question is waiting"
    detail = alert.title or fallback_detail
    session_url = f"{config.PUBLIC_URL}/?s={quote(alert.session_id)}"
    return headline, detail, session_url


def push_tag(session_id: SessionId) -> str:
    """Return the push tag.

    The notification tag a pushed alert is shown under — the ONE encoding of
        it, shared by the sender, the retraction and the service worker (sw.js
        builds the same string). It is what makes a repeat alert REPLACE its
        predecessor instead of stacking, and what the resolve push closes.

    Returns:
        Push tag.

    """
    return "baqylau-%s" % (session_id or "")
