"""
Helpers for persisting local-only application settings.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Mapping

from src.common.app_paths import local_settings_path

DEFAULT_LOCAL_SETTINGS_PATH = local_settings_path()


def load_local_settings(path: str | Path | None = None) -> dict:
    path = Path(path) if path is not None else local_settings_path()
    if not path.is_file():
        return {}

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}

    if not isinstance(payload, dict):
        return {}
    return payload


def filter_local_settings(
    config: Mapping[str, object],
    allowed_keys: Iterable[str],
) -> dict[str, object]:
    allowed = set(allowed_keys)
    return {
        key: config[key]
        for key in sorted(allowed)
        if key in config
    }


def save_local_settings(
    config: Mapping[str, object],
    allowed_keys: Iterable[str],
    path: str | Path | None = None,
) -> dict[str, object]:
    payload = filter_local_settings(config, allowed_keys)
    path = Path(path) if path is not None else local_settings_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return payload
