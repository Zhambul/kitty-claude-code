# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide standard dependencies."""

import json as json
import os as os
import sqlite3 as sqlite3
import subprocess as subprocess  # noqa: S404 -- Expose process results and errors for foundation tests.
import typing as typing
from collections.abc import Callable as Callable, Mapping as Mapping, Sequence as Sequence
from dataclasses import dataclass as dataclass, replace as replace
from pathlib import Path as Path

import pytest as pytest
