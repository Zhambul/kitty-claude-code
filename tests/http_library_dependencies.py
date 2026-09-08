# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide http library dependencies."""

import http as http
import typing as typing
from pathlib import Path as Path
from types import MappingProxyType as MappingProxyType
from urllib.parse import quote as quote

import fastapi as fastapi
import pytest as pytest
import uvicorn as uvicorn
from pydantic import TypeAdapter as TypeAdapter

from api.app import build_web_application as build_web_application
