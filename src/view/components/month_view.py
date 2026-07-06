from __future__ import annotations

from PyQt6.QtCore import QDate, QRectF, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QPainter
from PyQt6.QtWidgets import QWidget


class MonthView(QWidget):
    """单月日历视图。"""

    dateClicked = pyqtSignal(QDate)
    hoveredDateChanged = pyqtSignal(QDate)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_date = QDate.currentDate()
        self.start_date = None
        self.end_date = None
        self.hover_date = None
        self.setMouseTracking(True)
        self.setFixedSize(280, 240)

    def set_month(self, year: int, month: int):
        self.current_date = QDate(year, month, 1)
        self.update()

    def set_range(self, start, end, hover=None):
        self.start_date = start
        self.end_date = end
        self.hover_date = hover
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        self._paint_week_header(painter)
        self._paint_days(painter)

    def _paint_week_header(self, painter: QPainter):
        painter.setFont(QFont("Microsoft YaHei", 9))
        painter.setPen(QColor("#999"))

        cell_width = self.width() / 7
        for index, week_name in enumerate(["一", "二", "三", "四", "五", "六", "日"]):
            painter.drawText(
                QRectF(index * cell_width, 0, cell_width, self._cell_height()),
                Qt.AlignmentFlag.AlignCenter,
                week_name,
            )

    def _paint_days(self, painter: QPainter):
        first_day = QDate(self.current_date.year(), self.current_date.month(), 1)
        start_date = first_day.addDays(-(first_day.dayOfWeek() - 1))
        cell_width = self.width() / 7
        cell_height = self._cell_height()

        painter.setFont(QFont("Microsoft YaHei", 9))
        for row in range(6):
            for column in range(7):
                date = start_date.addDays(row * 7 + column)
                rect = QRectF(column * cell_width, (row + 1) * cell_height, cell_width, cell_height)
                self._paint_day_cell(painter, date, rect)

    def _paint_day_cell(self, painter: QPainter, date: QDate, rect: QRectF):
        is_current_month = date.month() == self.current_date.month()
        is_start = date == self.start_date
        is_end = date == self.end_date
        in_range = self._is_in_hover_or_selected_range(date)

        if in_range:
            painter.setBrush(QColor("#e6f4ff"))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(rect)
        elif is_start or is_end:
            painter.setBrush(QColor("#1890ff"))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(rect.adjusted(4, 4, -4, -4), 4, 4)

        if not is_current_month:
            painter.setPen(QColor("#ccc"))
        elif is_start or is_end:
            painter.setPen(QColor("white"))
        else:
            painter.setPen(QColor("#333"))
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, str(date.day()))

    def _is_in_hover_or_selected_range(self, date: QDate) -> bool:
        if not self.start_date:
            return False
        if self.end_date:
            return self.start_date < date < self.end_date
        if self.hover_date:
            start, end = sorted([self.start_date, self.hover_date])
            return start < date < end
        return False

    def mousePressEvent(self, event):
        date = self._date_at(event.position())
        if date:
            self.dateClicked.emit(date)

    def mouseMoveEvent(self, event):
        date = self._date_at(event.position())
        if date != self.hover_date:
            self.hover_date = date
            self.hoveredDateChanged.emit(date)

    def _date_at(self, pos):
        cell_width = self.width() / 7
        cell_height = self._cell_height()
        column = int(pos.x() // cell_width)
        row = int(pos.y() // cell_height) - 1
        if 0 <= row < 6 and 0 <= column < 7:
            first_day = QDate(self.current_date.year(), self.current_date.month(), 1)
            start_date = first_day.addDays(-(first_day.dayOfWeek() - 1))
            return start_date.addDays(row * 7 + column)
        return None

    @staticmethod
    def _cell_height() -> int:
        return 32
