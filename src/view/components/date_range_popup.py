from __future__ import annotations

from PyQt6.QtCore import QDate, Qt
from PyQt6.QtGui import QColor, QPainter, QPainterPath
from PyQt6.QtWidgets import (
    QDialog,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from .month_view import MonthView


class AntdDateRangePopup(QDialog):
    """Ant Design 风格双月选择弹出层。"""

    def __init__(self, start: QDate, end: QDate, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.start_date = start
        self.end_date = end
        self.hover_date = None
        self.view_date = QDate(start.year(), start.month(), 1)

        self._setup_ui()
        self._update_all()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor("white"))
        painter.setPen(QColor("#f0f0f0"))

        path = QPainterPath()
        path.moveTo(25, 10)
        path.lineTo(30, 2)
        path.lineTo(35, 10)
        path.closeSubpath()
        painter.drawPath(path)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(25, 9, 10, 2)

    def _setup_ui(self):
        self.container = QFrame(self)
        self.container.setStyleSheet(
            """
            QFrame {
                background: white; border-radius: 4px;
                border: 1px solid #f0f0f0;
            }
            """
        )
        self.container.setGraphicsEffect(self._create_shadow())

        main_layout = QVBoxLayout(self.container)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.addLayout(self._build_navigation())
        main_layout.addLayout(self._build_calendars())

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 10, 0, 10)
        layout.addWidget(self.container)

    def _create_shadow(self) -> QGraphicsDropShadowEffect:
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 4)
        return shadow

    def _build_navigation(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        self.btn_prev_y = self._nav_btn("<<")
        self.btn_prev_m = self._nav_btn("<")
        self.title_l = QLabel()
        self.title_r = QLabel()
        self.btn_next_m = self._nav_btn(">")
        self.btn_next_y = self._nav_btn(">>")

        layout.addWidget(self.btn_prev_y)
        layout.addWidget(self.btn_prev_m)
        layout.addStretch()
        layout.addWidget(self.title_l)
        layout.addStretch()
        layout.addWidget(self.title_r)
        layout.addStretch()
        layout.addWidget(self.btn_next_m)
        layout.addWidget(self.btn_next_y)

        self.btn_prev_y.clicked.connect(lambda: self._adj_view(years=-1))
        self.btn_prev_m.clicked.connect(lambda: self._adj_view(months=-1))
        self.btn_next_m.clicked.connect(lambda: self._adj_view(months=1))
        self.btn_next_y.clicked.connect(lambda: self._adj_view(years=1))
        return layout

    def _build_calendars(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        self.mv_left = MonthView()
        self.mv_right = MonthView()
        layout.addWidget(self.mv_left)
        layout.addWidget(self.mv_right)

        self.mv_left.dateClicked.connect(self._on_click)
        self.mv_right.dateClicked.connect(self._on_click)
        self.mv_left.hoveredDateChanged.connect(self._update_hovers)
        self.mv_right.hoveredDateChanged.connect(self._update_hovers)
        return layout

    def _nav_btn(self, text: str) -> QPushButton:
        button = QPushButton(text)
        button.setFixedSize(24, 24)
        button.setStyleSheet(
            "QPushButton { border:none; color:#999; font-weight:bold; } "
            "QPushButton:hover { color:#1890ff; }"
        )
        return button

    def _adj_view(self, years: int = 0, months: int = 0):
        self.view_date = self.view_date.addYears(years).addMonths(months)
        self._update_all()

    def _update_all(self):
        self.title_l.setText(f"{self.view_date.year()}年 {self.view_date.month()}月")
        next_month = self.view_date.addMonths(1)
        self.title_r.setText(f"{next_month.year()}年 {next_month.month()}月")

        self.mv_left.set_month(self.view_date.year(), self.view_date.month())
        self.mv_right.set_month(next_month.year(), next_month.month())
        self._refresh_ranges()

    def _update_hovers(self, hover: QDate):
        self.hover_date = hover
        self._refresh_ranges()

    def _refresh_ranges(self):
        self.mv_left.set_range(self.start_date, self.end_date, self.hover_date)
        self.mv_right.set_range(self.start_date, self.end_date, self.hover_date)

    def _on_click(self, date: QDate):
        if not self.start_date or (self.start_date and self.end_date):
            self.start_date = date
            self.end_date = None
        else:
            if date < self.start_date:
                self.start_date, self.end_date = date, self.start_date
            else:
                self.end_date = date
            self.accept()
        self.hover_date = None
        self._refresh_ranges()

    def get_range(self):
        return self.start_date, self.end_date
