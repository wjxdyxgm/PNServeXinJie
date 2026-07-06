from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from src.view.components import VerticalProgressBar


class GasStatusPanel(QFrame):
    PRIMARY = "#597EF7"
    OK_GREEN = "#389E0D"
    NG_RED = "#D4380D"
    PROGRESS_NG = "#CF1322"
    GREY_BG = "#C4C4C4"

    clearStatisticsRequested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(180)
        self.setStyleSheet("background: transparent;")
        self._build_ui()
        self.set_status_card("pending")

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.status_frame = QFrame()
        self.status_frame.setFixedHeight(80)
        status_layout = QVBoxLayout(self.status_frame)
        status_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.status_icon_label = QLabel("--")
        self.status_icon_label.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
        self.status_icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.status_text_label = QLabel("待检测")
        self.status_text_label.setStyleSheet(
            "color: white; font-size: 22px; font-weight: 900; font-family: 'YouSheBiaoTiHei';"
        )
        self.status_text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_layout.addWidget(self.status_icon_label)
        status_layout.addWidget(self.status_text_label)
        layout.addWidget(self.status_frame)

        bars_frame = QFrame()
        bars_frame.setStyleSheet("background: white; border-radius: 6px;")
        bars_layout = QHBoxLayout(bars_frame)
        bars_layout.setContentsMargins(8, 8, 8, 8)
        bars_layout.setSpacing(8)

        ok_column = QVBoxLayout()
        ok_column.setSpacing(4)
        self.ok_bar = VerticalProgressBar(0, self.OK_GREEN, self.GREY_BG)
        ok_column.addWidget(self.ok_bar, 1)
        ok_title = QLabel("合格")
        ok_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ok_count_label = QLabel("0")
        self.ok_count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ok_count_label.setStyleSheet(
            f"color: {self.OK_GREEN}; font-size: 18px; font-weight: bold; font-family: 'YouSheBiaoTiHei';"
        )
        ok_column.addWidget(ok_title)
        ok_column.addWidget(self.ok_count_label)
        bars_layout.addLayout(ok_column)

        ng_column = QVBoxLayout()
        ng_column.setSpacing(4)
        self.ng_bar = VerticalProgressBar(0, self.PROGRESS_NG, self.GREY_BG)
        ng_column.addWidget(self.ng_bar, 1)
        ng_title = QLabel("不合格")
        ng_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ng_count_label = QLabel("0")
        self.ng_count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ng_count_label.setStyleSheet(
            f"color: {self.PROGRESS_NG}; font-size: 18px; font-weight: bold; font-family: 'YouSheBiaoTiHei';"
        )
        ng_column.addWidget(ng_title)
        ng_column.addWidget(self.ng_count_label)
        bars_layout.addLayout(ng_column)

        layout.addWidget(bars_frame, 1)

        clear_btn = QPushButton("统计清零")
        clear_btn.setFixedHeight(48)
        clear_btn.setStyleSheet(
            f"background: {self.PRIMARY}; color: white; border: none; border-radius: 6px; "
            "font-size: 18px; font-weight: bold; font-family: 'YouSheBiaoTiHei';"
        )
        clear_btn.clicked.connect(lambda checked=False: self.clearStatisticsRequested.emit())
        layout.addWidget(clear_btn)

    def update_statistics(self, ok_count: int, ng_count: int):
        total_count = ok_count + ng_count
        if total_count > 0:
            ok_percent = round(ok_count / total_count * 100)
            ng_percent = 100 - ok_percent
        else:
            ok_percent = 0
            ng_percent = 0

        self.ok_bar.value = ok_percent
        self.ng_bar.value = ng_percent
        self.ok_bar.update()
        self.ng_bar.update()
        self.ok_count_label.setText(str(ok_count))
        self.ng_count_label.setText(str(ng_count))

    def set_status_card(self, status_state: str):
        if status_state == "ok":
            background = self.OK_GREEN
            title = "合格"
            icon = "OK"
        elif status_state == "ng":
            background = self.NG_RED
            title = "不合格"
            icon = "NG"
        else:
            background = "#8C8C8C"
            title = "待检测"
            icon = "--"

        self.status_frame.setStyleSheet(f"background-color: {background}; border-radius: 6px;")
        self.status_icon_label.setText(icon)
        self.status_text_label.setText(title)
