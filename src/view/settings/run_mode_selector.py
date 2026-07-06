from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QButtonGroup, QHBoxLayout, QPushButton, QWidget

from src.store.settings_store import RUN_MODE_OPTIONS


class RunModeSelector(QWidget):
    """运行模式分段按钮组。"""

    modeSelected = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.buttons: dict[int, QPushButton] = {}
        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)
        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet("background: transparent;")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        modes = sorted(RUN_MODE_OPTIONS.items())
        count = len(modes)
        for index, (mode, label) in enumerate(modes):
            button = QPushButton(label)
            button.setCheckable(True)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setFixedSize(92, 34)
            button.setStyleSheet(self._button_style(index, count))
            button.toggled.connect(lambda checked, btn=button: btn.raise_() if checked else None)
            button.clicked.connect(lambda checked=False, selected=mode: self.modeSelected.emit(selected))

            self.button_group.addButton(button, mode)
            self.buttons[mode] = button
            layout.addWidget(button)

        layout.addStretch()

    def set_mode(self, mode: int):
        button = self.buttons.get(mode)
        if button and not button.isChecked():
            button.setChecked(True)

    @staticmethod
    def _button_style(index: int, count: int) -> str:
        if count == 1:
            radius = "border-radius: 4px;"
        elif index == 0:
            radius = "border-top-left-radius: 4px; border-bottom-left-radius: 4px; border-top-right-radius: 0px; border-bottom-right-radius: 0px;"
        elif index == count - 1:
            radius = "border-top-left-radius: 0px; border-bottom-left-radius: 0px; border-top-right-radius: 4px; border-bottom-right-radius: 4px;"
        else:
            radius = "border-radius: 0px;"

        margin = "margin-left: -1px;" if index > 0 else ""
        return f"""
            QPushButton {{
                background: #ffffff;
                border: 1px solid #d9d9d9;
                {radius}
                {margin}
                color: #555;
                font-size: 14px;
            }}
            QPushButton:hover {{
                color: #1890ff;
            }}
            QPushButton:checked {{
                background: #1890ff;
                border-color: #1890ff;
                color: white;
            }}
            """
