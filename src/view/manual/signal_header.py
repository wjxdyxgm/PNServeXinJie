from __future__ import annotations

from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QWidget

from src.view.components import StatusLamp


DEFAULT_SIGNAL_NAMES = ["顶缸上限", "顶缸下限", "销钉1", "销钉2", "OK", "NG"]


class SignalHeader(QWidget):
    """手动模式顶部信号指示栏。"""

    def __init__(self, signal_names=None, parent=None):
        super().__init__(parent)
        self.signal_lamps = {}
        self._build_ui(signal_names or DEFAULT_SIGNAL_NAMES)

    def _build_ui(self, signal_names):
        layout = QHBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("信号指示")
        title.setStyleSheet("font-weight: bold; font-size: 16px; margin-right: 10px;")
        layout.addWidget(title)

        for name in signal_names:
            layout.addWidget(self._create_signal_item(name))

        layout.addStretch()

    def _create_signal_item(self, name: str) -> QFrame:
        item = QFrame()
        item.setStyleSheet("background: white; border-radius: 2px; padding: 2px 8px;")

        layout = QHBoxLayout(item)
        layout.setContentsMargins(4, 2, 4, 2)

        lamp = StatusLamp(size=12)
        self.signal_lamps[name] = lamp

        label = QLabel(name)
        label.setStyleSheet("font-size: 13px; color: #333;")

        layout.addWidget(lamp)
        layout.addWidget(label)
        return item

    def update_signals(self, signals: dict):
        for name, state in signals.items():
            lamp = self.signal_lamps.get(name)
            if not lamp:
                continue
            if name == "NG":
                lamp.set_error(state)
            else:
                lamp.set_active(state)
