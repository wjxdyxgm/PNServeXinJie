from __future__ import annotations

import os


def debug_log(message: str) -> None:
    """Print debug logs only when explicitly enabled."""

    if os.environ.get("PNSERVEX_DEBUG", "").lower() in {"1", "true", "yes", "on"}:
        print(message)
