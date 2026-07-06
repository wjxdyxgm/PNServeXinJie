from __future__ import annotations

from datetime import datetime

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from src.view.components import CapsuleToggle


class HeaderBar(QFrame):
    HEADER_BG = "#597EF7"

    tabChanged = pyqtSignal(int)
    minimizeRequested = pyqtSignal()
    maximizeRequested = pyqtSignal()
    closeRequested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.labels: dict[str, QLabel] = {}
        self._build_ui()

    def _build_ui(self):
        self.setFixedHeight(60)
        self.setStyleSheet(f"background-color: {self.HEADER_BG};")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 0, 0)
        layout.setSpacing(0)

        logo = QLabel("精驰")
        logo.setStyleSheet(
            """
            color: white; font-size: 20pt; font-weight: 900;
            font-family: 'YouSheBiaoTiHei', 'Microsoft YaHei';
            background: transparent;
            padding: 0 5px;
            """
        )
        layout.addWidget(logo)

        layout.addSpacing(25)
        self.capsule = CapsuleToggle([("手动", "manual"), ("自动", "gas"), ("设置", "settings")])
        self.capsule.tabChanged.connect(self.tabChanged)
        layout.addWidget(self.capsule)
        layout.addStretch()

        self.system_time_label = QLabel()
        self.system_time_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.system_time_label.setStyleSheet(
            """
            color: white; font-size: 14px; font-weight: bold;
            font-family: 'YouSheBiaoTiHei', sans-serif;
            margin-right: 15px;
            """
        )
        layout.addWidget(self.system_time_label)

        for title, value in [("上班", "00:00"), ("操作数", "0")]:
            column = QVBoxLayout()
            column.setContentsMargins(0, 5, 0, 5)
            column.setSpacing(0)

            title_label = QLabel(title)
            title_label.setStyleSheet(
                "color: rgba(255, 255, 255, 0.7); font-size: 13px; font-family: 'YouSheBiaoTiHei';"
            )
            title_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

            value_label = QLabel(value)
            value_label.setStyleSheet(
                """
                color: white; font-size: 24px; font-weight: bold;
                font-family: 'YouSheBiaoTiHei';
                """
            )
            value_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.labels[title] = value_label

            column.addWidget(title_label)
            column.addWidget(value_label)

            wrapper = QWidget()
            wrapper.setFixedWidth(100)
            wrapper.setLayout(column)
            layout.addWidget(wrapper)

        layout.addSpacing(15)
        layout.addWidget(self._build_window_controls())

    def _build_window_controls(self) -> QWidget:
        right_controls = QWidget()
        right_layout = QVBoxLayout(right_controls)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        win_layout = QHBoxLayout()
        win_layout.setSpacing(0)
        self.min_btn = self._create_win_btn("\uE921")
        self.max_btn = self._create_win_btn("\uE922")
        self.close_btn = self._create_win_btn("\uE8BB", is_close=True)

        self.min_btn.clicked.connect(lambda checked=False: self.minimizeRequested.emit())
        self.max_btn.clicked.connect(lambda checked=False: self.maximizeRequested.emit())
        self.close_btn.clicked.connect(lambda checked=False: self.closeRequested.emit())

        win_layout.addWidget(self.min_btn)
        win_layout.addWidget(self.max_btn)
        win_layout.addWidget(self.close_btn)

        right_layout.addLayout(win_layout)
        right_layout.addStretch()
        return right_controls

    def _create_win_btn(self, text: str, is_close: bool = False) -> QPushButton:
        button = QPushButton(text)
        button.setFixedSize(46, 32)
        hover_color = "#e81123" if is_close else "rgba(255, 255, 255, 0.2)"
        button.setStyleSheet(
            f"""
            QPushButton {{
                background: transparent; color: white; border: none; font-size: 10pt;
                font-family: 'Segoe Fluent Icons', 'Segoe MDL2 Assets', sans-serif;
            }}
            QPushButton:hover {{
                background: {hover_color};
            }}
            """
        )
        return button

    def set_system_time(self, date_text: str, time_text: str):
        self.system_time_label.setText(f"{date_text}\n{time_text}")

    def set_auth_summary(self, clock_in_time: float, operation_count: int):
        if clock_in_time > 0:
            dt = datetime.fromtimestamp(clock_in_time)
            self.labels["上班"].setText(dt.strftime("%H:%M"))
        else:
            self.labels["上班"].setText("--:--")

        self.labels["操作数"].setText(str(operation_count))

    def set_maximized_icon(self, maximized: bool):
        self.max_btn.setText("\uE923" if maximized else "\uE922")
