from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QGridLayout, QPushButton, QWidget


class NumericKeyGrid(QWidget):
    """数字键盘按键网格。"""

    keyClicked = pyqtSignal(str)

    KEYS = [
        ("7", 0, 0), ("8", 0, 1), ("9", 0, 2),
        ("4", 1, 0), ("5", 1, 1), ("6", 1, 2),
        ("1", 2, 0), ("2", 2, 1), ("3", 2, 2),
        (".", 3, 0), ("0", 3, 1), ("←", 3, 2),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        for text, row, column in self.KEYS:
            button = QPushButton(text)
            button.setFixedSize(85, 60)
            button.clicked.connect(lambda checked=False, value=text: self.keyClicked.emit(value))
            layout.addWidget(button, row, column)
