from __future__ import annotations

import math

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QPushButton, QWidget


class PaginationControls(QWidget):
    """页码按钮组。"""

    PRIMARY = "#597EF7"

    pageRequested = pyqtSignal(int)
    previousRequested = pyqtSignal()
    nextRequested = pyqtSignal()

    def __init__(self, visible_pages: int = 5, parent=None):
        super().__init__(parent)
        self.page_buttons = []
        self.visible_pages = visible_pages
        self._build_ui()

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        self.prev_page_btn = self._create_page_button("<")
        self.prev_page_btn.clicked.connect(lambda checked=False: self.previousRequested.emit())
        layout.addWidget(self.prev_page_btn)

        for _ in range(self.visible_pages):
            button = self._create_page_button("")
            button.clicked.connect(self._on_page_button_clicked)
            self.page_buttons.append(button)
            layout.addWidget(button)

        self.next_page_btn = self._create_page_button(">")
        self.next_page_btn.clicked.connect(lambda checked=False: self.nextRequested.emit())
        layout.addWidget(self.next_page_btn)

    def refresh(self, total_count: int, current_page: int, page_size: int) -> int:
        total_pages = max(1, math.ceil(total_count / page_size))
        current_page = min(current_page, total_pages)

        self.prev_page_btn.setEnabled(current_page > 1)
        self.next_page_btn.setEnabled(current_page < total_pages)

        start_page = max(1, current_page - 2)
        end_page = min(total_pages, start_page + len(self.page_buttons) - 1)
        start_page = max(1, end_page - len(self.page_buttons) + 1)

        pages = list(range(start_page, end_page + 1))
        while len(pages) < len(self.page_buttons):
            pages.append(None)

        for button, page_number in zip(self.page_buttons, pages):
            self._set_button_page(button, page_number, current_page)

        return current_page

    def _set_button_page(self, button: QPushButton, page_number: int | None, current_page: int):
        if page_number is None:
            button.setText("")
            button.setEnabled(False)
            self._style_page_button(button, active=False)
            return

        button.setText(str(page_number))
        button.setEnabled(True)
        self._style_page_button(button, active=page_number == current_page)

    def _create_page_button(self, text: str) -> QPushButton:
        button = QPushButton(text)
        button.setFixedSize(30, 30)
        self._style_page_button(button)
        return button

    def _style_page_button(self, button: QPushButton, active: bool = False):
        if active:
            button.setStyleSheet(
                f"background: {self.PRIMARY}; color: white; border: none; border-radius: 2px; font-weight: bold;"
            )
        else:
            button.setStyleSheet(
                "background: white; color: #666; border: 1px solid #ddd; border-radius: 2px;"
            )

    def _on_page_button_clicked(self):
        button = self.sender()
        if not isinstance(button, QPushButton):
            return

        text = button.text().strip()
        if text.isdigit():
            self.pageRequested.emit(int(text))
