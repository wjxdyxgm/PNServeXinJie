from __future__ import annotations

from collections.abc import Callable
from datetime import datetime

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QHeaderView, QPushButton, QTableWidget, QTableWidgetItem

from src.store.gas_store import GasStore


class GasRecordsTable(QTableWidget):
    """气检记录表格，负责行数据渲染和曲线图按钮。"""

    PRIMARY = "#597EF7"
    OK_GREEN = "#389E0D"
    NG_RED = "#D4380D"
    IMAGE_COLUMN = 21

    chartImageRequested = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(0, 22, parent)
        self._configure()
        self.fill_records([], lambda _path: False)

    def _configure(self):
        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setStretchLastSection(True)
        header.setMinimumSectionSize(70)
        header.hide()

        self.verticalHeader().setVisible(False)
        self.verticalHeader().setDefaultSectionSize(36)
        self.setShowGrid(False)
        self.setMinimumHeight(120)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.setStyleSheet(
            """
            QTableWidget { background: white; border: none; }
            QTableWidget::item { border-bottom: 1px solid #F0F0F0; padding: 4px; }
            QTableWidget::item:selected { background: #E6F4FF; color: #333; }
            """
        )

        column_widths = [
            56, 146, 190, 110, 86,
            84, 84, 84, 84,
            84, 84, 84, 84,
            84, 84, 84, 84,
            84, 84, 84, 84,
            92,
        ]
        for index, width in enumerate(column_widths):
            self.setColumnWidth(index, width)

    def fill_records(self, records: list[dict], image_exists: Callable[[str], bool]):
        self._clear_cell_widgets()
        self.clearContents()
        self.setRowCount(len(records))

        result_cols = {4, 6, 8, 10, 12, 14, 16, 18, 20}
        gas_result_col = 4

        for row, record in enumerate(records):
            row_data = self._record_to_row_data(record)
            is_gas_ng = row_data[gas_result_col] == "NG"

            for col, value in enumerate(row_data):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self._apply_result_style(item, col, value, result_cols, is_gas_ng)
                self.setItem(row, col, item)

            image_path = record.get("chart_image") or ""
            self.setCellWidget(
                row,
                self.IMAGE_COLUMN,
                self._create_chart_button(image_path, enabled=bool(image_path) and image_exists(image_path)),
            )

    def _clear_cell_widgets(self):
        for row in range(self.rowCount()):
            widget = self.cellWidget(row, self.IMAGE_COLUMN)
            if widget is not None:
                widget.deleteLater()

    def _record_to_row_data(self, record: dict) -> list[str]:
        return [
            str(record.get("id", "")),
            self._format_timestamp(record.get("timestamp", "")),
            record.get("product_code", ""),
            record.get("operator", ""),
            GasStore.result_to_text(record.get("airtight", 0)),
            self._format_float(record.get("pin1_pressure")),
            GasStore.result_to_text(record.get("pin1_pressure_result", 0)),
            self._format_float(record.get("pin1_distance")),
            GasStore.result_to_text(record.get("pin1_distance_result", 0)),
            self._format_float(record.get("pin2_pressure")),
            GasStore.result_to_text(record.get("pin2_pressure_result", 0)),
            self._format_float(record.get("pin2_distance")),
            GasStore.result_to_text(record.get("pin2_distance_result", 0)),
            self._format_float(record.get("pin3_pressure")),
            GasStore.result_to_text(record.get("pin3_pressure_result", 0)),
            self._format_float(record.get("pin3_distance")),
            GasStore.result_to_text(record.get("pin3_distance_result", 0)),
            self._format_float(record.get("pin4_pressure")),
            GasStore.result_to_text(record.get("pin4_pressure_result", 0)),
            self._format_float(record.get("pin4_distance")),
            GasStore.result_to_text(record.get("pin4_distance_result", 0)),
        ]

    def _apply_result_style(
        self,
        item: QTableWidgetItem,
        col: int,
        value: str,
        result_cols: set[int],
        is_gas_ng: bool,
    ):
        if is_gas_ng:
            item.setForeground(QColor(self.NG_RED))
        elif col in result_cols and value == "NG":
            item.setForeground(QColor(self.NG_RED))
            font = item.font()
            font.setBold(True)
            item.setFont(font)
        elif col in result_cols and value == "OK":
            item.setForeground(QColor(self.OK_GREEN))
        elif col in result_cols and value == "未记录":
            item.setForeground(QColor("#BFBFBF"))

    def _create_chart_button(self, image_path: str, enabled: bool) -> QPushButton:
        button = QPushButton("查看" if enabled else "无图")
        button.setEnabled(enabled)
        if enabled:
            button.setStyleSheet(
                f"QPushButton {{ background: {self.PRIMARY}; color: white; border: none; "
                f"border-radius: 4px; padding: 4px 12px; margin: 4px 10px; }}"
            )
            button.clicked.connect(lambda checked=False, path=image_path: self.chartImageRequested.emit(path))
        else:
            button.setStyleSheet(
                "QPushButton { background: #F5F5F5; color: #BFBFBF; border: 1px solid #E8E8E8; "
                "border-radius: 4px; padding: 4px 12px; margin: 4px 10px; }"
            )
        return button

    @staticmethod
    def _format_timestamp(value: str) -> str:
        if not value:
            return ""
        try:
            return datetime.fromisoformat(value).strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            return value

    @staticmethod
    def _format_float(value) -> str:
        if value in (None, ""):
            return ""
        try:
            return f"{float(value):.3f}".rstrip("0").rstrip(".")
        except (TypeError, ValueError):
            return ""

    @staticmethod
    def header_groups():
        return [
            {"label": "ID", "span": 1},
            {"label": "时间", "span": 1},
            {"label": "产品码", "span": 1},
            {"label": "操作员", "span": 1},
            {"label": "气密结果", "span": 1},
            {
                "label": "销钉1",
                "span": 4,
                "subs": ["压力值", "压力结果", "距离值", "距离结果"],
            },
            {
                "label": "销钉2",
                "span": 4,
                "subs": ["压力值", "压力结果", "距离值", "距离结果"],
            },
            {
                "label": "销钉3",
                "span": 4,
                "subs": ["压力值", "压力结果", "距离值", "距离结果"],
            },
            {
                "label": "销钉4",
                "span": 4,
                "subs": ["压力值", "压力结果", "距离值", "距离结果"],
            },
            {"label": "曲线图", "span": 1},
        ]
