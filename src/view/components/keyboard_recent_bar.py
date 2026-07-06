from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QWidget


class KeyboardRecentBar(QWidget):
    """虚拟键盘最近输入快捷栏。"""

    nameSelected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(10)
        self.layout.addStretch()

    def set_names(self, names: list[str]):
        self._clear_items()
        if names:
            title = QLabel("最近输入：")
            title.setStyleSheet("color: #888; font-size: 14px; font-weight: bold;")
            self.layout.insertWidget(0, title)

        for name in reversed(names):
            button = QPushButton(name)
            button.setStyleSheet(
                """
                QPushButton {
                    background: #E6F4FF; color: #1890FF; border: 1px solid #91CAFF;
                    border-radius: 4px; padding: 2px 10px; font-size: 16px;
                    min-height: 25px;
                }
                QPushButton:hover { background: #BAE7FF; }
                """
            )
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.clicked.connect(lambda checked=False, value=name: self.nameSelected.emit(value))
            self.layout.insertWidget(self.layout.count() - 1, button)

    def _clear_items(self):
        while self.layout.count() > 1:
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
