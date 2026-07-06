"""
Runtime path helpers for source mode and frozen executables.
"""
from __future__ import annotations

import sys
from pathlib import Path


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[2]


def app_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return workspace_root()


def data_dir(create: bool = False) -> Path:
    path = app_root() / "data"
    if create:
        path.mkdir(parents=True, exist_ok=True)
    return path


def image_dir(create: bool = False) -> Path:
    path = data_dir(create=create) / "image"
    if create:
        path.mkdir(parents=True, exist_ok=True)
    return path


def log_dir(create: bool = False) -> Path:
    path = app_root() / "log"
    if create:
        path.mkdir(parents=True, exist_ok=True)
    return path


def gas_records_db_path() -> Path:
    return app_root() / "gas_records.db"


def local_settings_path() -> Path:
    return data_dir() / "local_settings.json"


def dev_config_path() -> Path:
    return app_root() / "dev_config.json"
