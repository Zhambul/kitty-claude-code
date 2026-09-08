# Copyright (c) 2026 Zhambyl Yermagambet
"""Notification processing for the public notifier facade."""

from __future__ import annotations

import time
import typing
from operator import itemgetter
from pathlib import Path

from dashboard import config
from notify import notifier_processing_services as services
from notify.channels import alert, retraction, telegram, webpush

notifier_models = services.notifier_models
notification_audit = services.audit
routing = services.routing
NOTIFICATION_RETRY_SECONDS = 1.0

if typing.TYPE_CHECKING:
    import threading

    from domain.actor_state import ActorStatus
    from domain.ids import SessionId
    from notify import notifier_dependencies, presence


class _NotifierOperations(typing.Protocol):
    """Describe later notifier stages used by earlier stages."""

    def deliver_due(self, current_states: dict[SessionId, ActorStatus | None], now: float) -> None:
        """Deliver every notification that is due."""

    def resolve(
        self, session_id: SessionId, current_actor_status: ActorStatus | None, now: float, badge: int = 0,
    ) -> None:
        """Resolve notifications that no longer apply."""

    def schedule(
        self, alertable: notifier_models.Alertable, actor_status: ActorStatus, kind: str, now: float,
    ) -> None:
        """Schedule one new notification."""

    def escalate(self, notification: notifier_models.PendingNotification) -> None:
        """Escalate one pushed notification."""

    def suppress(self, notification: notifier_models.PendingNotification) -> None:
        """Suppress one notification."""

    def route_notification(
        self,
        notification: notifier_models.PendingNotification,
        current_states: dict[SessionId, ActorStatus | None],
        now: float,
    ) -> None:
        """Route one notification to a channel."""

    def track(
        self,
        pending_notification: notifier_models.PendingNotification,
        delivery_handle: retraction.NotificationHandle | None,
    ) -> None:
        """Track one delivered notification."""


class _NotifierState:
    """Store the dependencies and notification state."""

    def __init__(
        self,
        dependencies: notifier_dependencies.NotifierDependencies,
    ) -> None:
        """Initialize the object."""
        self._read_model = dependencies.session_data_repository
        self._terminal = dependencies.terminal_adapter
        self._repositories = dependencies.repository_queries
        self._notification_state = dependencies.dashboard_notification_state
        self._notification_settings = dependencies.notification_setting_repository
        self._push_subscriptions = dependencies.push_subscription_repository
        self._push_signing_keys = dependencies.push_signing_key_repository
        self._presence = dependencies.presence
        self._audit = dependencies.audit_recorder
        self._changes = dependencies.changes
        self._wake: threading.Event | None = None
        # One query per pass, not one per armed session.
        self._muted: frozenset[SessionId] = frozenset()
        self.previous_states: dict[SessionId, ActorStatus | None] | None = None
        self.pending: dict[SessionId, notifier_models.PendingNotification] = {}
        self.delivered: dict[SessionId, list[notifier_models.DeliveredNotification]] = {}

    def _operations(self) -> _NotifierOperations:
        return typing.cast("_NotifierOperations", self)


class _NotifierScan(_NotifierState):
    """Read session state and find notification changes."""

    def scan(self) -> None:
        # ATTENDED sessions only: a notification is a nudge back to a window,
        # and a parked session has none to nudge you to.
        """Scan."""
        notifier = self._operations()
        alertable_sessions = self._alertable_sessions()
        current_states = {alertable.session_id: alertable.status for alertable in alertable_sessions}
        self._muted = self._notification_settings.muted_session_ids()
        if self.previous_states is None:
            self.previous_states = current_states
            return
        now = time.monotonic()
        badge = notifier_models.attention_count(current_states)
        self._resolve_changes(alertable_sessions, current_states, now, badge)
        self._resolve_stale_deliveries(current_states, now, badge)
        self.previous_states = current_states
        notifier.deliver_due(current_states, now)

    def _next_delay(self) -> float | None:
        now = time.monotonic()
        delays = [
            max(0, notification.due_at - now)
            for notification in self.pending.values()
        ]
        states = self.previous_states or {}
        if any(
            notification.state != states.get(session_id)
            for session_id, delivered in self.delivered.items()
            for notification in delivered
        ):
            delays.append(NOTIFICATION_RETRY_SECONDS)
        return min(delays, default=None)

    def _alertable_sessions(self) -> tuple[notifier_models.Alertable, ...]:
        visible = self._read_model.lead_sessions()
        attended = self._terminal.live_sessions(session_record.session.session_id for session_record in visible)
        return tuple(
            notifier_models.Alertable(
                session_id=session_record.session.session_id,
                title=session_record.session.title or "",
                project=Path(
                    self._repositories.project_directory(session_record.session.working_directory) or "",
                ).name
                or str(session_record.session.session_id),
                status=None if session_record.lead is None else session_record.lead.status,
            )
            for session_record in visible
            if session_record.session.session_id in attended
        )

    def _resolve_changes(
        self,
        alertable_sessions: tuple[notifier_models.Alertable, ...],
        current_states: dict[SessionId, ActorStatus | None],
        now: float,
        badge: int,
    ) -> None:
        alertable_by_session = {alertable.session_id: alertable for alertable in alertable_sessions}
        for session_id in set(self.previous_states or ()) | set(current_states):
            self._resolve_change(
                session_id,
                current_states.get(session_id),
                alertable_by_session,
                now,
                badge,
            )

    def _resolve_change(
        self,
        session_id: SessionId,
        actor_status: ActorStatus | None,
        alertable_by_session: dict[SessionId, notifier_models.Alertable],
        now: float,
        badge: int,
    ) -> None:
        notifier = self._operations()
        if (self.previous_states or {}).get(session_id) == actor_status:
            return
        notifier.resolve(session_id, actor_status, now, badge)
        if actor_status is None:
            return
        notification_kind = notifier_models.NOTIFICATION_KINDS.get(actor_status)
        alertable = alertable_by_session.get(session_id)
        if notification_kind is not None and alertable is not None:
            notifier.schedule(alertable, actor_status, notification_kind, now)

    def _resolve_stale_deliveries(
        self,
        current_states: dict[SessionId, ActorStatus | None],
        now: float,
        badge: int,
    ) -> None:
        notifier = self._operations()
        for session_id, delivered in list(self.delivered.items()):
            if any(
                delivered_notification.state != current_states.get(session_id) for delivered_notification in delivered
            ):
                notifier.resolve(
                    session_id,
                    current_states.get(session_id),
                    now,
                    badge,
                )


class _NotifierScheduling(_NotifierScan):
    """Schedule notifications that need delivery."""

    def schedule(
        self, alertable: notifier_models.Alertable, actor_status: ActorStatus, kind: str, now: float,
    ) -> None:
        """Publish a notification and set its delivery deadline."""
        session_id = alertable.session_id
        if not self._notification_settings.alerting_enabled() or session_id in self._muted:
            return
        project = alertable.project
        title = alertable.title
        self._notification_state.publish_notification(session_id, kind, project, title)
        delay = config.NOTIFICATION_DELAY_SECONDS
        if kind == "done":
            delay = max(delay, config.NOTIFICATION_SETTLE_SECONDS)
        self.pending[session_id] = notifier_models.PendingNotification(
            session_id,
            actor_status,
            kind,
            project,
            title,
            now + delay,
        )

    def deliver_due(
        self,
        current_states: dict[SessionId, ActorStatus | None],
        now: float,
    ) -> None:
        """Deliver due notifications and remove notifications for stale states."""
        for session_id, notification in list(self.pending.items()):
            self._deliver_pending(session_id, notification, current_states, now)

    def _deliver_pending(
        self,
        session_id: SessionId,
        notification: notifier_models.PendingNotification,
        current_states: dict[SessionId, ActorStatus | None],
        now: float,
    ) -> None:
        if current_states.get(session_id) == notification.state:
            self._deliver_current(notification, current_states, now)
        else:
            self.pending.pop(session_id, None)

    def _deliver_current(
        self,
        notification: notifier_models.PendingNotification,
        current_states: dict[SessionId, ActorStatus | None],
        now: float,
    ) -> None:
        if now >= notification.due_at:
            self._deliver_ready(notification, current_states, now)

    def _deliver_ready(
        self,
        notification: notifier_models.PendingNotification,
        current_states: dict[SessionId, ActorStatus | None],
        now: float,
    ) -> None:
        notifier = self._operations()
        if notification.pushed:
            notifier.escalate(notification)
        elif self._presence.web_viewing(notification.session_id) or self._presence.device_active():
            notifier.suppress(notification)
        else:
            notifier.route_notification(notification, current_states, now)


class _NotifierDelivery(_NotifierScheduling):
    """Route notifications to the available delivery channel."""

    def escalate(self, notification: notifier_models.PendingNotification) -> None:
        """Send a second alert through Telegram if the session is not viewed."""
        # Stage 2: the routed browser push has had its chance. If the session
        # still needs attention, Telegram is the nudge on another channel.
        notifier = self._operations()
        self.pending.pop(notification.session_id, None)
        if not self._presence.web_viewing(notification.session_id) and config.NOTIFY_TELEGRAM:
            notifier.track(
                notification,
                telegram.send_alert(notification.payload(), "escalation"),
            )

    def suppress(self, notification: notifier_models.PendingNotification) -> None:
        """Remove a pending notification and record its suppression."""
        self.pending.pop(notification.session_id, None)
        self._audit.state_file(
            "",
            "",
            "notification-suppressed",
            notification_audit.NotificationSuppressedAudit(
                session_id=notification.session_id,
                kind=notification.kind,
                reason="browser-present",
            ),
        )

    def route_notification(
        self,
        notification: notifier_models.PendingNotification,
        current_states: dict[SessionId, ActorStatus | None],
        now: float,
    ) -> None:
        """Send a browser push or use the configured Telegram fallback."""
        payload = notification.payload()
        target, subscriptions, decision = routing.route(self._presence, self._push_subscriptions)
        self._audit_route(notification, decision)
        push_handle = self._push_handle(payload, subscriptions, current_states)
        if push_handle is not None:
            self._finish_push(notification, payload, push_handle, now)
            return
        self._fallback(notification, payload, target, subscriptions)

    def _audit_route(
        self,
        notification: notifier_models.PendingNotification,
        decision: presence.RouteDecision,
    ) -> None:
        self._audit.state_file(
            "",
            "",
            "notification-route",
            notification_audit.NotificationRouteAudit(
                target=decision.target,
                target_label=decision.target_label,
                subscription_count=decision.subscription_count,
                candidates=tuple(
                    notification_audit.NotificationRouteCandidateAudit(
                        device=candidate.device,
                        label=candidate.label,
                        age_s=candidate.age_s,
                    )
                    for candidate in decision.candidates
                ),
                session_id=notification.session_id,
                kind=notification.kind,
            ),
        )

    def _push_handle(
        self,
        payload: alert.Alert,
        subscriptions: list[presence.RoutedSubscription],
        current_states: dict[SessionId, ActorStatus | None],
    ) -> retraction.NotificationHandle | None:
        if not subscriptions or not config.NOTIFY_WEBPUSH:
            return None
        return webpush.send_alert(
            payload,
            subscriptions,
            notifier_models.attention_count(current_states),
            push_signing_key_repository=self._push_signing_keys,
            push_subscription_repository=self._push_subscriptions,
        )

    def _finish_push(
        self,
        notification: notifier_models.PendingNotification,
        payload: alert.Alert,
        push_handle: retraction.NotificationHandle,
        now: float,
    ) -> None:
        notifier = self._operations()
        notifier.track(notification, push_handle)
        if config.NOTIFY_TELEGRAM_ALWAYS:
            self.pending.pop(notification.session_id, None)
            if config.NOTIFY_TELEGRAM:
                notifier.track(notification, telegram.send_alert(payload, "always"))
        elif config.NOTIFY_TELEGRAM:
            notification.pushed = True
            notification.due_at = now + config.ESCALATION_DELAY_SECONDS
        else:
            self.pending.pop(notification.session_id, None)

    def _fallback(
        self,
        notification: notifier_models.PendingNotification,
        payload: alert.Alert,
        target: str | None,
        subscriptions: list[presence.RoutedSubscription],
    ) -> None:
        notifier = self._operations()
        self.pending.pop(notification.session_id, None)
        if not config.NOTIFY_TELEGRAM:
            return
        if target == "terminal":
            reason = "terminal"
        elif subscriptions:
            reason = "push-off"
        else:
            reason = "no-device"
        notifier.track(notification, telegram.send_alert(payload, reason))


class _NotifierRetraction(_NotifierDelivery):
    """Track delivered notifications and retract stale alerts."""

    def track(
        self,
        pending_notification: notifier_models.PendingNotification,
        delivery_handle: retraction.NotificationHandle | None,
    ) -> None:
        """Store a delivered notification so it can be retracted later."""
        if delivery_handle is None:
            return
        self.delivered.setdefault(pending_notification.session_id, []).append(
            notifier_models.DeliveredNotification(
                pending_notification.session_id,
                pending_notification.state,
                delivery_handle,
                time.monotonic(),
            ),
        )
        self._enforce_sent_cap()

    def resolve(
        self,
        session_id: SessionId,
        current_actor_status: ActorStatus | None,
        now: float,
        badge: int = 0,
    ) -> None:
        """Cancel pending delivery and retract alerts for an old actor state."""
        self.pending.pop(session_id, None)
        delivered = self.delivered.get(session_id) or []
        remaining = [
            notification
            for notification in delivered
            if self._delivery_remains(notification, current_actor_status, now, badge)
        ]
        if remaining:
            self.delivered[session_id] = remaining
        else:
            self.delivered.pop(session_id, None)

    def _delivery_remains(
        self,
        notification: notifier_models.DeliveredNotification,
        current_actor_status: ActorStatus | None,
        now: float,
        badge: int,
    ) -> bool:
        if notification.state == current_actor_status:
            return True
        age = now - notification.delivered_at
        if age >= config.RETRACTION_LIFETIME_SECONDS:
            self._audit_retraction(notification, "expired", age)
            return False
        outcome = retraction.retract(
            notification.notification_handle,
            badge=badge,
            push_signing_key_repository=self._push_signing_keys,
            push_subscription_repository=self._push_subscriptions,
        )
        if outcome in {alert.PENDING, alert.FAILED}:
            return True
        self._audit_retraction(notification, outcome, age)
        return False

    def _audit_retraction(
        self,
        delivered_notification: notifier_models.DeliveredNotification,
        outcome: str,
        age: float,
        reason: str = "state-changed",
    ) -> None:
        self._audit.state_file(
            "",
            "",
            "notify-retract",
            notification_audit.NotificationRetractionAudit(
                session_id=delivered_notification.session_id,
                channel=delivered_notification.notification_handle.ch,
                kind=delivered_notification.notification_handle.kind,
                reason=reason,
                outcome=outcome,
                age_seconds=round(max(0, age), 3),
            ),
        )

    def _enforce_sent_cap(self) -> None:
        excess = sum(map(len, self.delivered.values())) - config.SENT_CAP
        if excess <= 0:
            return
        oldest = sorted(
            (
                (notification.delivered_at, session_id, notification)
                for session_id, delivered in self.delivered.items()
                for notification in delivered
            ),
            key=itemgetter(0),
        )[:excess]
        for _, session_id, notification in oldest:
            delivered = self.delivered.get(session_id) or []
            if notification not in delivered:
                continue
            delivered.remove(notification)
            self._audit_retraction(
                notification,
                "capacity-expired",
                time.monotonic() - notification.delivered_at,
                "capacity",
            )
