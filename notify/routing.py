# Copyright (c) 2026 Zhambyl Yermagambet
"""Select the most recently seen notification device."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import TYPE_CHECKING

from domain.ids import DeviceId
from notify import presence as subscription_models
from notify.presence import (
    DEVICE_FIELD,
    LABEL_FIELD,
    NEVER_SEEN,
    TERMINAL,
    Presence,
    RouteCandidate,
    RouteDecision,
    RoutedSubscription,
)

if TYPE_CHECKING:
    from repository.contract.preferences import PushSubscriptionRepository


@dataclass(frozen=True)
class RouteBuilder:
    """Build a routing decision from presence and subscriptions."""

    presence: Presence
    subscriptions: list[RoutedSubscription]
    now: float
    terminal_seen: float

    @classmethod
    def from_repository(
        cls,
        presence: Presence,
        push_subscription_repository: PushSubscriptionRepository,
    ) -> RouteBuilder:
        """Build routing data from the subscription store.

        Returns:
            The route builder.

        """
        subscriptions: list[RoutedSubscription] = [
            RoutedSubscription(
                endpoint=subscription.endpoint,
                device=subscription.device_id,
                label=subscription.device_label,
                keys=subscription_models.SubscriptionKeys(
                    p256dh=subscription.public_key, auth=subscription.authentication_secret,
                ),
            )
            for subscription in push_subscription_repository.subscriptions()
        ]
        return cls(presence, subscriptions, time.monotonic(), presence.last_seen(TERMINAL))

    def candidate(self, device_id: DeviceId, label: str | None = None) -> RouteCandidate:
        """Build one route candidate.

        Returns:
            The route candidate.

        """
        seen_at = self.presence.last_seen(device_id)
        return RouteCandidate(
            device=device_id,
            label=label,
            age_s=None if seen_at == NEVER_SEEN else round(self.now - seen_at, 1),
        )

    def candidates(self) -> list[RouteCandidate]:
        """Build all route candidates.

        Returns:
            The route candidates.

        """
        candidates = [
            self.candidate(DeviceId(subscription[DEVICE_FIELD]), subscription.get(LABEL_FIELD))
            for subscription in self.subscriptions
        ]
        if self.terminal_seen != NEVER_SEEN:
            candidates.append(self.candidate(DeviceId(TERMINAL), "terminal"))
        return candidates

    def decision(self, target: str | None, label: str | None = None) -> RouteDecision:
        """Build the final route decision.

        Returns:
            The route decision.

        """
        return RouteDecision(
            target=target,
            target_label=label,
            subscription_count=len(self.subscriptions),
            candidates=self.candidates(),
        )


def route(
    presence: Presence,
    push_subscription_repository: PushSubscriptionRepository,
) -> tuple[str | None, list[RoutedSubscription], RouteDecision]:
    """Select the most recently seen notification device.

    Returns:
        The target, its subscriptions, and the route decision.

    """
    routing = RouteBuilder.from_repository(presence, push_subscription_repository)
    best = max(
        (subscription[DEVICE_FIELD] for subscription in routing.subscriptions),
        key=presence.last_seen,
        default=None,
    )
    if best is not None and presence.last_seen(best) >= routing.terminal_seen:
        targets = [subscription for subscription in routing.subscriptions if subscription[DEVICE_FIELD] == best]
        return best, targets, routing.decision(best, targets[0].get(LABEL_FIELD))
    if routing.terminal_seen == NEVER_SEEN:
        return None, [], routing.decision(None)
    return TERMINAL, [], routing.decision(TERMINAL, "terminal")
