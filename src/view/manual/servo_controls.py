from __future__ import annotations

from PyQt6.QtWidgets import QCheckBox, QHBoxLayout, QPushButton, QWidget

from src.view.manual.servo_card_styles import (
    FAULT_RESET_BUTTON_STYLE,
    HOME_ACTIVE_STYLE,
    HOME_INACTIVE_STYLE,
    RUN_BUTTON_STYLE,
)


class ServoControls(QWidget):
    """伺服卡控制按钮区。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.enable_cb = QCheckBox("使能")
        layout.addWidget(self.enable_cb)

        self.home_btn = QPushButton("回零")
        self.home_btn.setFixedSize(70, 32)
        self.set_home_active(True)
        layout.addWidget(self.home_btn)

        self.fault_reset_btn = QPushButton("故障复位")
        self.fault_reset_btn.setFixedSize(90, 32)
        self.fault_reset_btn.setStyleSheet(FAULT_RESET_BUTTON_STYLE)
        layout.addWidget(self.fault_reset_btn)

        self.run_btn = QPushButton("启动运行")
        self.run_btn.setFixedHeight(32)
        self.run_btn.setStyleSheet(RUN_BUTTON_STYLE)
        layout.addWidget(self.run_btn, 1)

    def set_home_active(self, active: bool):
        self.home_btn.setStyleSheet(HOME_ACTIVE_STYLE if active else HOME_INACTIVE_STYLE)

    def set_enabled_checked(self, enabled: bool):
        self.enable_cb.blockSignals(True)
        self.enable_cb.setChecked(enabled)
        self.enable_cb.blockSignals(False)
