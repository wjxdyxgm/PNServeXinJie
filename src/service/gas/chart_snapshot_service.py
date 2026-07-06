from __future__ import annotations

from .chart_image_service import GasChartImageService


class GasChartSnapshotService:
    """保存气检曲线截图，并把图片路径回写到记录。"""

    def __init__(self, image_service: GasChartImageService):
        self._image_service = image_service

    def save_and_attach(
        self,
        pixmap,
        store,
        record_id: int,
        product_code: str,
        timestamp: str,
    ) -> str:
        relative_path = ""
        try:
            relative_path = self._image_service.save_chart_image(
                pixmap,
                record_id,
                product_code,
                timestamp,
            )
            if relative_path:
                self._update_record_image(store, record_id, relative_path)
        except Exception as exc:
            self._image_service.log_error(
                "save_chart",
                record_id=record_id,
                image_path=relative_path,
                error=exc,
            )
        return relative_path

    def _update_record_image(self, store, record_id: int, relative_path: str) -> None:
        try:
            store.update_chart_image(record_id, relative_path)
        except Exception as exc:
            self._image_service.log_error(
                "update_chart_image",
                record_id=record_id,
                image_path=relative_path,
                error=exc,
            )
