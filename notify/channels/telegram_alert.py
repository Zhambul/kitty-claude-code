# Copyright (c) 2026 Zhambyl Yermagambet
"""Send and retract Telegram alerts outside the watcher thread."""

import dataclasses
import threading
import time
from typing import TYPE_CHECKING, Literal

from audit import record as audit_record
from notify.audit import NotificationSessionAudit
from notify.channel_audit import TelegramRetractionAudit, TelegramSendAudit
from notify.channels import telegram_api, telegram_credentials
from notify.channels.alert import FAILED, GONE, NOTHING, OK, PENDING, Alert, alert_text

if TYPE_CHECKING:
    from domain.ids import SessionId

RETRACTION_RETRY_SECONDS = 30.0


@dataclasses.dataclass
class TelegramHandle:
    """Hold the shared send and retraction state for one message."""

    ch: Literal["telegram"] = "telegram"
    session_id: "SessionId | None" = None
    kind: str | None = None
    chat: int | str | None = None
    msg_id: int | None = None
    done: bool = False
    outcome: str | None = None
    retry_at: float = 0
    deleting: bool = False


def send_alert(alert: Alert, reason: str | None = None) -> TelegramHandle | None:
    """Start an off-thread Telegram send.

    Returns:
        The mutable retraction handle, or None when Telegram is disabled.

    """
    message = _telegram_message(alert)
    if not telegram_credentials.enabled():
        return None
    telegram_handle = TelegramHandle(
        session_id=alert.session_id,
        kind=alert.kind,
    )
    sender = threading.Thread(
        target=_telegram_send_body,
        args=(telegram_handle, message, reason),
        daemon=True,
    )
    sender.start()
    return telegram_handle


def _telegram_message(alert: Alert) -> str:
    head, title, url = alert_text(alert)
    return f"{head} — {title}\n{url}"


def _telegram_send_body(
    telegram_handle: TelegramHandle,
    message: str,
    reason: str | None,
) -> None:
    try:
        response = telegram_api.send_message(message)
    except (OSError, RuntimeError, ValueError):
        audit_record.error(
            "",
            "dashboard telegram notify",
            NotificationSessionAudit(session_id=telegram_handle.session_id),
        )
        telegram_handle.done = True
        return
    if response.ok:
        telegram_handle.chat = response.chat
        telegram_handle.msg_id = response.message_id
    audit_record.state_file(
        "",
        "",
        "telegram-notify",
        TelegramSendAudit(
            session_id=telegram_handle.session_id,
            kind=telegram_handle.kind,
            reason=reason,
            ok=response.ok,
            status=response.status,
            error=response.error,
            retractable=bool(response.ok and response.message_id),
            message_id=response.message_id,
        ),
    )
    telegram_handle.done = True


def retract_alert(
    telegram_handle: TelegramHandle,
) -> str:
    """Start or poll an off-thread Telegram retraction.

    Returns:
        The current retraction outcome.

    """
    if not telegram_handle.done:
        return PENDING
    if telegram_handle.outcome in {OK, GONE}:
        return str(telegram_handle.outcome)
    if telegram_handle.outcome == FAILED:
        if time.monotonic() < telegram_handle.retry_at:
            return PENDING
        telegram_handle.outcome = None
        telegram_handle.deleting = False
    if not (telegram_handle.chat and telegram_handle.msg_id):
        return NOTHING
    if not telegram_handle.deleting:
        telegram_handle.deleting = True
        threading.Thread(
            target=_telegram_delete_body,
            args=(telegram_handle,),
            daemon=True,
        ).start()
    return PENDING


def _telegram_delete_body(telegram_handle: TelegramHandle) -> None:
    try:
        response = telegram_api.delete_message(
            telegram_handle.chat,
            telegram_handle.msg_id,
        )
    except (OSError, RuntimeError, ValueError):
        _record_delete_exception(telegram_handle)
        return
    if response.ok:
        outcome = OK
    elif response.gone:
        outcome = GONE
    else:
        outcome = FAILED
    if outcome == FAILED:
        telegram_handle.retry_at = time.monotonic() + RETRACTION_RETRY_SECONDS
    telegram_handle.outcome = outcome
    audit_record.state_file(
        "",
        "",
        "telegram-retract",
        TelegramRetractionAudit(
            session_id=telegram_handle.session_id,
            kind=telegram_handle.kind,
            message_id=telegram_handle.msg_id,
            outcome=outcome,
            status=response.status,
            error=response.error,
        ),
    )


def _record_delete_exception(telegram_handle: TelegramHandle) -> None:
    audit_record.error(
        "",
        "dashboard telegram retract",
        NotificationSessionAudit(session_id=telegram_handle.session_id),
    )
    telegram_handle.retry_at = time.monotonic() + RETRACTION_RETRY_SECONDS
    telegram_handle.outcome = FAILED
    audit_record.state_file(
        "",
        "",
        "telegram-retract",
        TelegramRetractionAudit(
            session_id=telegram_handle.session_id,
            kind=telegram_handle.kind,
            message_id=telegram_handle.msg_id,
            outcome=FAILED,
            status=0,
            error="exception",
        ),
    )
