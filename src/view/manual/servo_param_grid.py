from __future__ import annotations

from PyQt6.QtWidgets import QGridLayout, QLabel, QWidget

from src.view.components import ClickableLineEdit
from src.view.manual.servo_card_styles import POSITION_FEEDBACK_STYLE, UNIT_LABEL_STYLE


class ServoParamGrid(QWidget):
    """伺服参数输入和反馈区。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        layout.addWidget(QLabel("伸出高度:"), 0, 0)
        self.pos_input = ClickableLineEdit("0")
        self.pos_input.setFixedWidth(80)
        layout.addWidget(self.pos_input, 0, 1)
        layout.addWidget(self._unit_label("mm"), 0, 2)

        layout.addWidget(QLabel("速度:"), 1, 0)
        self.mdi_input = ClickableLineEdit("0")
        self.mdi_input.setFixedWidth(80)
        layout.addWidget(self.mdi_input, 1, 1)

        layout.addWidget(QLabel("位置反馈:"), 0, 3)
        self.pos_fb = QLabel("0.000")
        self.pos_fb.setStyleSheet(POSITION_FEEDBACK_STYLE)
        layout.addWidget(self.pos_fb, 0, 4)
        layout.addWidget(self._unit_label("mm"), 0, 5)

        layout.addWidget(QLabel("零位补偿:"), 1, 3)
        self.zero_offset_input = ClickableLineEdit("0")
        self.zero_offset_input.setFixedWidth(80)
        layout.addWidget(self.zero_offset_input, 1, 4)
        layout.addWidget(self._unit_label("mm"), 1, 5)

    def set_values(self, data: dict):
        current_pos = data.get("current_pos", 0)
        self.pos_fb.setText(f"{float(current_pos) / 1000:.3f}")
        self._set_line_edit(self.pos_input, data.get("target_pos", 0))
        self._set_line_edit(self.mdi_input, data.get("mdi", 0))
        self._set_line_edit(self.zero_offset_input, data.get("zero_offset", 0.0))

    @staticmethod
    def _unit_label(text: str) -> QLabel:
        label = QLabel(text)
        label.setStyleSheet(UNIT_LABEL_STYLE)
        return label

    @staticmethod
    def _set_line_edit(line_edit: ClickableLineEdit, value):
        line_edit.blockSignals(True)
        line_edit.setText(str(value))
        line_edit.blockSignals(False)
