from __future__ import annotations

from PyQt6.QtWidgets import QGridLayout, QPushButton, QWidget

from .button_bindings import BUTTON_BINDING_MAP


class ManualButtonGrid(QWidget):
    """手动模式的 PLC 脉冲按钮网格。"""

    BUTTON_STYLE = """
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FFFFFF, stop:1 #E0E0E0);
            border: 1px solid #C0C0C0;
            border-radius: 8px;
            font-size: 18px;
            font-weight: bold;
            font-family: 'Microsoft YaHei';
            color: #333;
            min-height: 50px;
        }
        QPushButton:pressed {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #E0E0E0, stop:1 #D0D0D0);
        }
    """

    def __init__(self, store=None, parent=None):
        super().__init__(parent)
        self.store = store
        self._build_ui()

    def _build_ui(self):
        grid = QGridLayout(self)
        grid.setSpacing(15)
        grid.setContentsMargins(0, 0, 0, 0)

        button_names = self.store.button_actions if self.store else list(BUTTON_BINDING_MAP.keys())
        for index, text in enumerate(button_names):
            button = QPushButton(text)
            button.setStyleSheet(self.BUTTON_STYLE)
            self._connect_button(button, text)
            grid.addWidget(button, index // 4, index % 4)

    def _connect_button(self, button: QPushButton, text: str):
        if not self.store:
            return

        binding_path = BUTTON_BINDING_MAP.get(text, "")
        if binding_path:
            button.pressed.connect(lambda path=binding_path: self.store.write_plc(path, True))
            button.released.connect(lambda path=binding_path: self.store.write_plc(path, False))
            return

        button.clicked.connect(lambda _checked=False, action=text: self.store.execute_action(action))
