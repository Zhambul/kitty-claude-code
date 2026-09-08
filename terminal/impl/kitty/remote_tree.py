# Copyright (c) 2026 Zhambyl Yermagambet
"""Define typed kitty window-tree rows."""

from pydantic import BaseModel, ConfigDict

FOREIGN = ConfigDict(extra="ignore", frozen=True)


class KittyProcess(BaseModel):
    """Represent a kitty process."""

    model_config = FOREIGN
    pid: int | None = None
    cmdline: list[str] | None = None


class KittyWindowInfo(BaseModel):
    """Represent a kitty window."""

    model_config = FOREIGN
    id: int | str | None = None
    columns: int | None = None
    lines: int | None = None
    user_vars: dict[str, str] | None = None
    foreground_processes: list[KittyProcess] | None = None
    is_active: bool | None = None


class KittyTab(BaseModel):
    """Represent a kitty tab."""

    model_config = FOREIGN
    id: int | str | None = None
    is_active: bool | None = None
    is_focused: bool | None = None
    windows: list[KittyWindowInfo] | None = None


class KittyOSWindow(BaseModel):
    """Represent a kitty operating-system window."""

    model_config = FOREIGN
    is_focused: bool | None = None
    tabs: list[KittyTab] | None = None
