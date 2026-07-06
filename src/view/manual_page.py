from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QScrollArea
)
from PyQt6.QtCore import Qt

from src.view.manual import ManualButtonGrid, ServoCard, SignalHeader


class ManualPage(QFrame):
    """手动模式页面 — 包含按钮矩阵和伺服控制"""

    def __init__(self, store=None, parent=None):
        super().__init__(parent)
        self.store = store
        self.signal_header = None
        self.setStyleSheet("background: #f0f2f5;")
        self._build_ui()
        self._connect_signals()

    def _build_ui(self):
        main_lay = QVBoxLayout(self)
        main_lay.setContentsMargins(15, 15, 15, 15)
        main_lay.setSpacing(15)

        signal_names = list(self.store.signals) if self.store else None
        self.signal_header = SignalHeader(signal_names)
        main_lay.addWidget(self.signal_header)

        # 2. 中间按钮矩阵 (4列排布)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")
        
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        scroll_lay = QVBoxLayout(scroll_content)
        scroll_lay.setContentsMargins(0, 0, 0, 0)
        scroll_lay.setSpacing(20)

        scroll_lay.addWidget(ManualButtonGrid(self.store))

        # 3. 底部伺服控制卡片 (水平滚动，支持触屏滑动)
        servo_scroll = QScrollArea()
        servo_scroll.setWidgetResizable(False)
        servo_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        servo_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        servo_scroll.setStyleSheet("""
            QScrollArea { background: transparent; border: none; }
            QScrollBar:horizontal {
                height: 8px; background: #e8e8e8; border-radius: 4px;
            }
            QScrollBar::handle:horizontal {
                background: #bbb; border-radius: 4px; min-width: 40px;
            }
            QScrollBar::handle:horizontal:hover { background: #999; }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }
        """)
        servo_scroll.setFixedHeight(220)

        servo_container = QWidget()
        servo_container.setStyleSheet("background: transparent;")
        servo_lay = QHBoxLayout(servo_container)
        servo_lay.setContentsMargins(0, 0, 0, 0)
        servo_lay.setSpacing(12)
        for sid, title in [(1, "伺服 1"), (2, "伺服 2"), (3, "伺服 3"), (4, "伺服 4")]:
            card = ServoCard(title, sid, self.store)
            card.setFixedWidth(460)
            servo_lay.addWidget(card)

        servo_container.setFixedWidth(
            460 * 4 + 12 * 3 + 4  # 卡片宽度 × 4 + 间距 × 3 + 余量
        )
        servo_scroll.setWidget(servo_container)
        scroll_lay.addWidget(servo_scroll)
        
        scroll_lay.addStretch()
        scroll.setWidget(scroll_content)
        main_lay.addWidget(scroll, 1)

    def _connect_signals(self):
        if not self.store: return
        self.store.dataChanged.connect(self._update_all_ui)
        self._update_all_ui()

    def _update_all_ui(self):
        """同步所有 Store 状态到 UI"""
        if not self.store: return
        
        if self.signal_header:
            self.signal_header.update_signals(self.store.signals)
