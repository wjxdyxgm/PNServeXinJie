from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path


class GasChartImageService:
    def __init__(self, project_root: str | Path):
        self._project_root = Path(project_root)

    def save_chart_image(
        self,
        pixmap,
        record_id: int,
        product_code: str,
        timestamp: str,
    ) -> str:
        relative_path, absolute_path = self.build_chart_image_path(
            record_id,
            product_code,
            timestamp,
        )
        absolute_path.parent.mkdir(parents=True, exist_ok=True)
        if not pixmap.save(str(absolute_path), "PNG"):
            self.log_error(
                "save_chart",
                record_id=record_id,
                image_path=relative_path,
                error="QPixmap.save returned False",
            )
            return ""
        return relative_path

    def build_chart_image_path(
        self,
        record_id: int,
        product_code: str,
        timestamp: str,
    ) -> tuple[str, Path]:
        safe_product_code = self._sanitize_product_code(product_code)
        parsed_timestamp = self._parse_record_timestamp(timestamp)
        relative_path = (
            Path("data")
            / "image"
            / f"{int(record_id)}_{safe_product_code}_{parsed_timestamp.strftime('%Y-%m-%d_%H-%M')}.png"
        )
        return relative_path.as_posix(), self._project_root / relative_path

    def resolve_image_path(self, stored_path: str | Path) -> Path:
        image_path = Path(stored_path)
        if image_path.is_absolute():
            return image_path
        return self._project_root / image_path

    def log_error(self, action: str, **context) -> None:
        log_dir = self._project_root / "log"
        log_dir.mkdir(parents=True, exist_ok=True)

        parts = [f"time={datetime.now().isoformat(timespec='seconds')}", f"action={action}"]
        for key, value in context.items():
            if value in (None, ""):
                continue
            if isinstance(value, Path):
                value = value.as_posix()
            elif isinstance(value, Exception):
                value = f"{type(value).__name__}: {value}"
            parts.append(f"{key}={str(value).replace(chr(10), ' | ')}")

        with (log_dir / "gas_page.log").open("a", encoding="utf-8") as handle:
            handle.write(" ".join(parts) + "\n")

    @staticmethod
    def _sanitize_product_code(product_code: str) -> str:
        safe_value = re.sub(r"[^A-Za-z0-9_-]+", "_", (product_code or "").strip()).strip("_")
        return safe_value or "unknown"

    @staticmethod
    def _parse_record_timestamp(timestamp: str) -> datetime:
        try:
            return datetime.fromisoformat(timestamp)
        except ValueError:
            return datetime.now()
