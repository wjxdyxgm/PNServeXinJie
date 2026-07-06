from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QWidget

from src.store.settings_store import LIMIT_SETTING_KEYS
from src.view.components import ClickableLineEdit
from src.view.settings.styles import create_settings_card


TORQUE_LIMIT_FIELDS = [
    ("扭力OK下限1", "torque_ok_low_1"),
    ("扭力OK上限1", "torque_ok_high_1"),
    ("扭力OK下限2", "torque_ok_low_2"),
    ("扭力OK上限2", "torque_ok_high_2"),
    ("扭力OK下限3", "torque_ok_low_3"),
    ("扭力OK上限3", "torque_ok_high_3"),
    ("扭力OK下限4", "torque_ok_low_4"),
    ("扭力OK上限4", "torque_ok_high_4"),
]

SERVO_DIST_LIMIT_FIELDS = [
    ("伺服距离OK下限1", "servo_dist_ok_low_1"),
    ("伺服距离OK上限1", "servo_dist_ok_high_1"),
    ("伺服距离OK下限2", "servo_dist_ok_low_2"),
    ("伺服距离OK上限2", "servo_dist_ok_high_2"),
    ("伺服距离OK下限3", "servo_dist_ok_low_3"),
    ("伺服距离OK上限3", "servo_dist_ok_high_3"),
    ("伺服距离OK下限4", "servo_dist_ok_low_4"),
    ("伺服距离OK上限4", "servo_dist_ok_high_4"),
]

LIMIT_FIELD_LABELS = {key: label for label, key in TORQUE_LIMIT_FIELDS + SERVO_DIST_LIMIT_FIELDS}


class LimitsSettingsPanel(QWidget):
    limitValueChanged = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.limit_inputs: dict[str, ClickableLineEdit] = {}
        self._build_ui()
        self.validate_definitions()

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        card = create_settings_card()
        layout.addWidget(card)

        grid = QGridLayout(card)
        grid.setContentsMargins(30, 30, 30, 30)
        grid.setHorizontalSpacing(40)
        grid.setVerticalSpacing(25)

        max_rows = max(len(TORQUE_LIMIT_FIELDS), len(SERVO_DIST_LIMIT_FIELDS))
        for row in range(max_rows):
            if row < len(TORQUE_LIMIT_FIELDS):
                left_label, left_key = TORQUE_LIMIT_FIELDS[row]
                grid.addWidget(QLabel(left_label), row, 0)
                grid.addWidget(self._create_limit_input(left_key), row, 1)

            if row < len(SERVO_DIST_LIMIT_FIELDS):
                right_label, right_key = SERVO_DIST_LIMIT_FIELDS[row]
                grid.addWidget(QLabel(right_label), row, 2)
                grid.addWidget(self._create_limit_input(right_key), row, 3)

        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(3, 1)

    def _create_limit_input(self, key: str) -> ClickableLineEdit:
        line_edit = ClickableLineEdit("0", keyboard_type="numeric")
        line_edit.setFixedWidth(120)
        line_edit.valueChanged.connect(lambda value, item_key=key: self.limitValueChanged.emit(item_key, value))
        self.limit_inputs[key] = line_edit
        return line_edit

    def set_config(self, config: dict):
        for key, line_edit in self.limit_inputs.items():
            display_str = (
                f"{config[key]:.2f}"
                if isinstance(config[key], float)
                else str(config[key])
            )
            if line_edit.text() != display_str:
                line_edit.blockSignals(True)
                line_edit.setText(display_str)
                line_edit.blockSignals(False)

    def validate_definitions(self):
        actual_keys = set(self.limit_inputs)
        expected_keys = set(LIMIT_SETTING_KEYS)
        if actual_keys == expected_keys:
            return

        missing = sorted(expected_keys - actual_keys)
        extra = sorted(actual_keys - expected_keys)
        raise ValueError(
            f"limit input definitions out of sync: missing={missing}, extra={extra}"
        )
