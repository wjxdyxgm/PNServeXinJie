from __future__ import annotations

from PyQt6.QtWidgets import QHBoxLayout, QLabel, QWidget

from src.view.components import StatusLamp
from src.view.manual.servo_card_styles import (
    BLUE_VALUE_STYLE,
    CODE_LABEL_STYLE,
    MUTED_LABEL_STYLE,
    TITLE_LABEL_STYLE,
)


class ServoHeader(QWidget):
    """伺服卡头部状态区。"""

    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self._build_ui(title)

    def _build_ui(self, title: str):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        title_label = QLabel(title)
        title_label.setStyleSheet(TITLE_LABEL_STYLE)
        layout.addWidget(title_label)

        error_label = QLabel("错误码:")
        error_label.setStyleSheet(MUTED_LABEL_STYLE)
        layout.addWidget(error_label)

        self.error_code = QLabel("0")
        self.error_code.setStyleSheet(CODE_LABEL_STYLE)
        layout.addWidget(self.error_code)

        abs_label = QLabel("编码器绝对值:")
        abs_label.setStyleSheet(MUTED_LABEL_STYLE)
        layout.addWidget(abs_label)

        self.abs_pos_value = QLabel("0")
        self.abs_pos_value.setStyleSheet(BLUE_VALUE_STYLE)
        layout.addWidget(self.abs_pos_value)

        layout.addStretch()
        self.state_lamp = StatusLamp(size=14)
        layout.addWidget(QLabel("运动状态"))
        layout.addWidget(self.state_lamp)

    def set_feedback(self, current_pos, error_id, done: bool):
        self.abs_pos_value.setText(str(current_pos))
        self.error_code.setText(str(error_id))
        if error_id != 0:
            self.state_lamp.set_error(True)
        else:
            self.state_lamp.set_active(done)
