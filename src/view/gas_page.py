from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QDate, Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QMessageBox,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from src.common.app_paths import app_root
from src.service.gas import (
    GasChartImageService,
    GasChartSnapshotService,
)
from src.store.gas_store import GasStore
from src.view.gas import (
    ChartImageDialog,
    GasChartPanel,
    GasExportAction,
    GasStatusPanel,
    GasTablePanel,
)
from src.view.components import (
    GripSplitterHandle,
)


class GasPage(QWidget):
    def __init__(
        self,
        store: GasStore | None = None,
        manual_store=None,
        project_root: str | Path | None = None,
        parent=None,
    ):
        super().__init__(parent)
        self.store = store
        self.manual_store = manual_store
        self._project_root = Path(project_root) if project_root is not None else app_root()
        self.start_date = QDate.currentDate().addDays(-7)
        self.end_date = QDate.currentDate()
        self._last_query_state = None
        self._chart_images = GasChartImageService(self._project_root)
        self._chart_snapshots = GasChartSnapshotService(self._chart_images)
        self._export_action = GasExportAction(self)
        self.setStyleSheet("background: transparent;")
        self._build_ui()
        self._connect_signals()

        if self.store and not any(self.store.date_range):
            self._sync_search_to_store()
        else:
            self._update_ui_from_store()

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.setHandleWidth(12)
        splitter.setStyleSheet("QSplitter::handle { background: transparent; }")
        splitter.addWidget(self._build_table_panel())
        splitter.addWidget(self._build_chart_panel())
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)

        handle = splitter.handle(1)
        grip = GripSplitterHandle(Qt.Orientation.Vertical, handle)
        grip_layout = QVBoxLayout(handle)
        grip_layout.setContentsMargins(0, 0, 0, 0)
        grip_layout.addWidget(grip)

        layout.addWidget(splitter, 1)
        layout.addWidget(self._build_right_panel())

    def _build_table_panel(self):
        self.table_panel = GasTablePanel(self.start_date, self.end_date)
        self.table_panel.searchRequested.connect(self._on_search_requested)
        self.table_panel.exportRequested.connect(self._on_export_clicked)
        self.table_panel.chartImageRequested.connect(self._show_chart_image)
        self.table_panel.pageRequested.connect(self._set_page)
        self.table_panel.previousPageRequested.connect(self._go_prev_page)
        self.table_panel.nextPageRequested.connect(self._go_next_page)
        return self.table_panel

    def _build_chart_panel(self):
        self.chart_panel = GasChartPanel()
        return self.chart_panel

    def _sample_torque_from_manual_store(self):
        if self.manual_store is None:
            return

        torque_1 = float(self.manual_store.torque_data.get("torque_1", 0.0))
        torque_2 = float(self.manual_store.torque_data.get("torque_2", 0.0))
        self.chart_panel.sample_torque(torque_1, torque_2)

    def _on_run_seq_changed(self, run_seq: int):
        self.chart_panel.handle_run_seq(run_seq)

    def _on_clear_statistics_clicked(self):
        if self.store is not None:
            self.store.reset_statistics()

    def _build_right_panel(self):
        self.status_panel = GasStatusPanel()
        self.status_panel.clearStatisticsRequested.connect(self._on_clear_statistics_clicked)
        return self.status_panel

    def _connect_signals(self):
        if not self.store:
            return

        self.store.dataChanged.connect(self._update_ui_from_store)
        self.store.recordInserted.connect(self._on_record_inserted)
        if self.manual_store is not None and hasattr(self.manual_store, "dataChanged"):
            self.manual_store.dataChanged.connect(self._sample_torque_from_manual_store)
        self.store.runSeqChanged.connect(self._on_run_seq_changed)

    def _sync_search_to_store(self):
        if not self.store:
            return

        keyword = self.table_panel.search_keyword()
        self._on_search_requested(keyword, self.start_date, self.end_date)

    def _on_search_requested(self, keyword: str, start: QDate, end: QDate):
        self.start_date = start
        self.end_date = end
        if self.store:
            self.store.set_search(
                keyword=keyword,
                date_start=start.toString("yyyy-MM-dd"),
                date_end=end.toString("yyyy-MM-dd"),
            )

    def _update_ui_from_store(self):
        if not self.store:
            return

        self.table_panel.set_search_keyword(self.store.search_keyword)

        start_text, end_text = self.store.date_range
        if start_text and end_text:
            start = QDate.fromString(start_text, "yyyy-MM-dd")
            end = QDate.fromString(end_text, "yyyy-MM-dd")
            if start.isValid() and end.isValid():
                self.start_date = start
                self.end_date = end
                self.table_panel.set_date_range(start, end)

        product_code = self.store.current_data.get("product_code") or "XXXX-XXXX-XXXX-XXXX"
        self.table_panel.set_product_code(product_code)
        self.status_panel.set_status_card(self.store.get_status_card_state())
        self._reload_records_if_needed()

        ok_count = int(self.store.current_data.get("count_ok", 0))
        ng_count = int(self.store.current_data.get("count_ng", 0))
        self.status_panel.update_statistics(ok_count, ng_count)

    def _on_record_inserted(self, record_id: int, product_code: str, timestamp: str):
        self.chart_panel.freeze(record_id)
        self._chart_snapshots.save_and_attach(
            self.chart_panel.grab_chart(),
            self.store,
            record_id,
            product_code,
            timestamp,
        )
        self._reload_records_if_needed(force=True)

    def _reload_records_if_needed(self, force: bool = False):
        if not self.store:
            return

        query_state = (
            self.store.search_keyword,
            self.store.date_range,
            self.store.page_index,
            self.store.page_size,
        )

        if force or query_state != self._last_query_state:
            records, total_count = self.store.load_records()
            current_page = self.table_panel.refresh_pagination(
                total_count,
                self.store.page_index,
                self.store.page_size,
            )
            if current_page != self.store.page_index:
                self.store.set_page(current_page)
                return
            self.table_panel.fill_records(records, self._chart_image_exists)
            self._last_query_state = query_state

    def _chart_image_exists(self, image_path: str) -> bool:
        return self._chart_images.resolve_image_path(image_path).is_file()

    def _show_chart_image(self, path: str) -> None:
        absolute_path = self._chart_images.resolve_image_path(path)
        if not absolute_path.is_file():
            self._chart_images.log_error("show_chart_image", image_path=path, error="image file not found")
            QMessageBox.information(self, "提示", "曲线图文件不存在或无法加载。")
            return

        pixmap = QPixmap(str(absolute_path))
        if pixmap.isNull():
            self._chart_images.log_error("show_chart_image", image_path=path, error="QPixmap is null")
            QMessageBox.information(self, "提示", "曲线图文件不存在或无法加载。")
            return

        ChartImageDialog(pixmap, self).exec()

    def _set_page(self, page: int):
        if not self.store:
            return
        self.store.set_page(page)

    def _go_prev_page(self):
        if self.store:
            self.store.set_page(max(1, self.store.page_index - 1))

    def _go_next_page(self):
        if self.store:
            self.store.set_page(self.store.page_index + 1)

    def _on_export_clicked(self):
        if not self.store:
            return
        self._export_action.export_records(
            self.store.load_all_records(),
            self.start_date,
            self.end_date,
        )
