# Copyright (c) 2026 Zhambyl Yermagambet
"""THE display name of a model — one owner per harness, applied at fold time.

Three surfaces used to derive a model's name independently: the catalog (the
picker), the actor row, and the feed entry. Each derived it from whatever
fields it held at that moment, so one model showed as "sonnet" in the picker,
"sonnet-5" on a refined actor, and either on an entry, depending on when it
was written. Now each harness names its models ONCE
(`HarnessPlugin.model_display`), the writers apply that answer when a fact
folds, and `rebuild` re-derives every historical row through the same
function — which is what makes a naming fix reach old sessions too.
"""

from __future__ import annotations

from dataclasses import replace
from types import MappingProxyType
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping

    from domain.ids import HarnessName
    from domain.references import ModelReference

EMPTY_DISPLAY_BY_HARNESS: Mapping[
    HarnessName,
    Callable[[ModelReference], str],
] = MappingProxyType({})


class ModelNaming:
    """Represent model naming.

    The per-harness namers, with the honest fallback for harnesses that
        declare none: the display the source gave, or the native id.
    """

    def __init__(
        self,
        display_by_harness: Mapping[
            HarnessName,
            Callable[[ModelReference], str],
        ]
        | None = None,
    ) -> None:
        """Initialize the object."""
        self.display_by_harness = display_by_harness or EMPTY_DISPLAY_BY_HARNESS

    def display(self, harness: HarnessName, model_reference: ModelReference) -> str:
        """Return the display.

        Returns:
            Display.

        """
        namer = self.display_by_harness.get(harness)
        if namer is not None:
            return namer(model_reference)
        return model_reference.display_name or model_reference.name

    def named(self, harness: HarnessName, model_reference: ModelReference) -> ModelReference:
        """Return the named.

        The same reference with its display settled — what the actor row
                stores, so every reader downstream shows the one name.

        Returns:
            Named.

        """
        return replace(
            model_reference,
            display_name=self.display(harness, model_reference),
        )
