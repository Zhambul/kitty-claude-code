# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide e2e application dependencies."""

import threading as threading
import time as time
import tomllib as tomllib
from pathlib import Path as Path
from typing import TYPE_CHECKING as TYPE_CHECKING, Literal as Literal

import pytest as pytest

from api.runtime import ApplicationConfig as ApplicationConfig
