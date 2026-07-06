from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QWidget

from src.view.components import ClickableLineEdit, StatusLamp


class FooterBar(QFrame):
    operatorChanged = pyqtSignal(str)
    logoutRequested = pyqtSignal()

    def __init__(self, current_user: str = "", parent=None):
        super().__init__(parent)
        self._build_ui(current_user)

    def _build_ui(self, current_user: str):
        self.setFixedHeight(36)
        self.setStyleSheet(
            """
            QFrame {
                background-color: #F5F5F7;
                border-top: 1px solid #E0E0E0;
            }
            """
        )
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(0)

        operator_label = QLabel("操作员")
        operator_label.setStyleSheet("color: #666; font-size: 13px; border: none; background: transparent;")
        layout.addWidget(operator_label)
        layout.addSpacing(5)

        self.op_input = ClickableLineEdit(current_user, keyboard_type="full")
        self.op_input.setPlaceholderText("输入操作员")
        self.op_input.setFixedWidth(100)
        self.op_input.setStyleSheet(
            """
            background: transparent; border: none;
            color: #1890FF;
            font-size: 14px; font-weight: bold;
            font-family: 'FangSong', 'STFangsong';
            """
        )
        self.op_input.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.op_input.valueChanged.connect(self.operatorChanged)
        layout.addWidget(self.op_input)

        layout.addSpacing(15)
        self.logout_btn = QPushButton("注销登录")
        self.logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.logout_btn.setStyleSheet(
            """
            QPushButton {
                background: transparent; color: #999;
                border: none; font-size: 12px; text-decoration: underline;
            }
            QPushButton:hover { color: #597EF7; }
            """
        )
        self.logout_btn.clicked.connect(lambda checked=False: self.logoutRequested.emit())
        layout.addWidget(self.logout_btn)

        layout.addStretch()
        layout.addWidget(self._build_value_group("压力1/2/3/4:", "0.00/0.00/0.00/0.00", "KG", "torque_value_label", "#2f54eb"))
        layout.addSpacing(10)
        layout.addWidget(self._build_value_group("伺服1/2/3/4:", "0.000/0.000/0.000/0.000", "mm", "servo_value_label", "#1890ff"))
        layout.addStretch()

        self.plc_status_lamp = StatusLamp(size=10)
        self.plc_status_lamp.set_error(True)
        plc_label = QLabel("PLC")
        plc_label.setStyleSheet("color: #666; font-size: 12px; border: none; background: transparent;")
        layout.addWidget(self.plc_status_lamp)
        layout.addSpacing(4)
        layout.addWidget(plc_label)

    def _build_value_group(self, title: str, default_value: str, unit: str, attr_name: str, color: str) -> QWidget:
        panel = QWidget()
        panel_layout = QHBoxLayout(panel)
        panel_layout.setContentsMargins(0, 0, 0, 0)
        panel_layout.setSpacing(18)

        group = QWidget()
        group_layout = QHBoxLayout(group)
        group_layout.setContentsMargins(0, 0, 0, 0)
        group_layout.setSpacing(8)

        title_label = QLabel(title)
        title_label.setStyleSheet(
            "color: #7a7a7a; font-size: 12px; border: none; background: transparent;"
        )

        value_label = QLabel(default_value)
        value_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        value_label.setStyleSheet(
            f"""
            color: {color};
            font-size: 14px;
            font-weight: bold;
            font-family: 'Consolas', 'Microsoft YaHei';
            border: none;
            background: transparent;
            """
        )
        setattr(self, attr_name, value_label)

        unit_label = QLabel(unit)
        unit_label.setStyleSheet(
            "color: #9a9a9a; font-size: 11px; border: none; background: transparent;"
        )

        group_layout.addWidget(title_label)
        group_layout.addWidget(value_label)
        group_layout.addWidget(unit_label)
        panel_layout.addWidget(group)
        return panel

    def set_operator(self, username: str):
        if self.op_input.text() != username:
            self.op_input.setText(username)

    def set_feedback_values(self, torque_values: tuple[float, float, float, float], servo_values: tuple[float, float, float, float]):
        self.torque_value_label.setText("/".join(f"{value:.2f}" for value in torque_values))
        self.servo_value_label.setText("/".join(f"{value:.3f}" for value in servo_values))

    def set_plc_connected(self, connected: bool):
        if connected:
            self.plc_status_lamp.set_active(True)
        else:
            self.plc_status_lamp.set_error(True)
