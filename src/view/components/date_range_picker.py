from __future__ import annotations

from PyQt6.QtCore import QDate, Qt, pyqtSignal
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel

from .date_range_popup import AntdDateRangePopup
from .month_view import MonthView


class AntdDateRangePicker(QFrame):
    """Ant Design 风格日期范围选择器控件。"""

    valueChanged = pyqtSignal(QDate, QDate)

    def __init__(self, start=None, end=None, parent=None):
        super().__init__(parent)
        self.start_date = start or QDate.currentDate().addDays(-7)
        self.end_date = end or QDate.currentDate()
        self.setFixedSize(260, 32)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._setup_ui()

    def _setup_ui(self):
        self.setObjectName("Picker")
        self._apply_style(active=False)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(12)

        self.lbl_start = QLabel(self.start_date.toString("yyyy-MM-dd"))
        arrow_label = QLabel("→")
        arrow_label.setStyleSheet("color: #bfbfbf;")
        self.lbl_end = QLabel(self.end_date.toString("yyyy-MM-dd"))
        icon = QLabel("📅")
        icon.setStyleSheet("color: #ccc; font-size: 14px;")

        layout.addWidget(self.lbl_start)
        layout.addWidget(arrow_label)
        layout.addWidget(self.lbl_end)
        layout.addStretch()
        layout.addWidget(icon)

    def _apply_style(self, active: bool):
        border_color = "#1890ff" if active else "#d9d9d9"
        self.setStyleSheet(
            f"""
            #Picker {{
                background: white; border: 1px solid {border_color}; border-radius: 2px;
            }}
            #Picker:hover {{ border-color: #40a9ff; }}
            QLabel {{ color: #555; font-size: 13px; font-family: 'Microsoft YaHei', 'Segoe UI'; }}
            """
        )

    def mousePressEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            return

        self._apply_style(active=True)
        popup = AntdDateRangePopup(self.start_date, self.end_date, self.window())
        pos = self.mapToGlobal(self.rect().bottomLeft())
        popup.move(pos.x(), pos.y() + 5)

        if popup.exec():
            start, end = popup.get_range()
            if start and end:
                self.set_date_range(start, end)
                self.valueChanged.emit(start, end)

        self._apply_style(active=False)

    def set_date_range(self, start: QDate, end: QDate):
        self.start_date = start
        self.end_date = end
        self.lbl_start.setText(start.toString("yyyy-MM-dd"))
        self.lbl_end.setText(end.toString("yyyy-MM-dd"))


__all__ = ["AntdDateRangePicker", "AntdDateRangePopup", "MonthView"]
