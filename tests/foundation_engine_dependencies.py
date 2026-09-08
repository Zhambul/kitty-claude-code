# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide engine dependencies."""

from engine.interpret.output_source import ShellOutputRawEventSource as ShellOutputRawEventSource
from engine.react.loop import ReactionLoop as ReactionLoop, ReactionLoopDependencies as ReactionLoopDependencies
from harness import contract as _harness_contract, registry as _harness_registry
from harness.models.controls import ControlRequest as ControlRequest
from harness.models.info import HarnessInfo as HarnessInfo
from harness.models.interrupts import InterruptRegistry as InterruptRegistry
from harness.models.raw_event_builders import output_location_raw_event as output_location_raw_event
from harness.models.session import Session as Session

harness_contract = _harness_contract
harness_registry = _harness_registry
