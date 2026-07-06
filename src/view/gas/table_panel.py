from __future__ import annotations

from PyQt6.QtCore import QDate, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from src.view.components import AntdDateRangePicker
from src.view.gas.pagination import PaginationControls
from src.view.gas.records_table import GasRecordsTable
from src.view.gas.table_header import GroupHeaderWidget


class GasTablePanel(QFrame):
    PRIMARY = "#597EF7"
    searchRequested = pyqtSignal(str, QDate, QDate)
    exportRequested = pyqtSignal()
    chartImageRequested = pyqtSignal(str)
    pageRequested = pyqtSignal(int)
    previousPageRequested = pyqtSignal()
    nextPageRequested = pyqtSignal()

    def __init__(self, start_date: QDate, end_date: QDate, parent=None):
        super().__init__(parent)
        self.start_date = start_date
        self.end_date = end_date
        self.setStyleSheet("background: white; border-radius: 4px;")
        self._build_ui()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(8, 8, 8, 4)
        outer.setSpacing(4)

        tools = QHBoxLayout()
        self.date_picker = AntdDateRangePicker(self.start_date, self.end_date)
        self.date_picker.valueChanged.connect(self._on_date_changed)
        tools.addWidget(self.date_picker)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("查询操作员/产品码")
        self.name_input.setFixedWidth(160)
        self.name_input.setStyleSheet(
            "border: 1px solid #ddd; border-radius: 4px; padding: 4px 8px; background: white;"
        )
        self.name_input.editingFinished.connect(self._emit_search_requested)
        tools.addWidget(self.name_input)
        tools.addStretch()

        self.code_lbl = QLabel("产品码：XXXX-XXXX-XXXX-XXXX")
        self.code_lbl.setStyleSheet(
            "font-size: 18px; font-weight: 900; font-family: 'YouSheBiaoTiHei';"
        )
        tools.addWidget(self.code_lbl)
        outer.addLayout(tools)

        self.table = GasRecordsTable()
        self.table.chartImageRequested.connect(self.chartImageRequested.emit)
        self.group_header = GroupHeaderWidget(self.table, GasRecordsTable.header_groups())
        outer.addWidget(self.group_header)
        outer.addWidget(self.table, 1)

        footer = QHBoxLayout()
        self._export_btn = QPushButton("导出")
        self._export_btn.setStyleSheet(
            f"background: {self.PRIMARY}; color: white; padding: 6px 20px; "
            "border-radius: 4px; font-weight: bold; border: none;"
        )
        self._export_btn.clicked.connect(lambda checked=False: self.exportRequested.emit())
        footer.addWidget(self._export_btn)
        footer.addStretch()

        self.pagination = PaginationControls()
        self.pagination.pageRequested.connect(self.pageRequested.emit)
        self.pagination.previousRequested.connect(self.previousPageRequested.emit)
        self.pagination.nextRequested.connect(self.nextPageRequested.emit)
        footer.addWidget(self.pagination)
        outer.addLayout(footer)

    def set_search_keyword(self, keyword: str):
        if self.name_input.text() != keyword:
            self.name_input.setText(keyword)

    def search_keyword(self) -> str:
        return self.name_input.text().strip()

    def set_date_range(self, start: QDate, end: QDate):
        self.start_date = start
        self.end_date = end
        self.date_picker.set_date_range(start, end)

    def set_product_code(self, product_code: str):
        self.code_lbl.setText(f"产品码：{product_code or 'XXXX-XXXX-XXXX-XXXX'}")

    def fill_records(self, records, image_exists):
        self.table.fill_records(records, image_exists)

    def refresh_pagination(self, total_count: int, current_page: int, page_size: int) -> int:
        return self.pagination.refresh(total_count, current_page, page_size)

    def _emit_search_requested(self):
        self.searchRequested.emit(
            self.name_input.text().strip(),
            self.start_date,
            self.end_date,
        )

    def _on_date_changed(self, start: QDate, end: QDate):
        self.start_date = start
        self.end_date = end
        self._emit_search_requested()
