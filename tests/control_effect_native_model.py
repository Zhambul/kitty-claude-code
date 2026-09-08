# Copyright (c) 2026 Zhambyl Yermagambet
"""Control effect native model."""

from __future__ import annotations

from dataclasses import dataclass

from harness.models import raw_events as raw_event_models


@dataclass(frozen=True)
class NativeStartSequence:
    """Hold resume, start, and exit translations for related native runs."""

    resumed: raw_event_models.TranslationResult
    native: raw_event_models.TranslationResult
    another_run: raw_event_models.TranslationResult
    native_end: raw_event_models.TranslationResult
    liveness_end: raw_event_models.TranslationResult
