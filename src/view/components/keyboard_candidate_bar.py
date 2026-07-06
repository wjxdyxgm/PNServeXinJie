from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget


class KeyboardCandidateBar(QWidget):
    """虚拟键盘拼音缓冲和候选词分页栏。"""

    candidateSelected = pyqtSignal(str)

    def __init__(self, page_size: int = 8, parent=None):
        super().__init__(parent)
        self.page_size = page_size
        self.candidates = []
        self.candidate_page = 0
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 0, 5, 0)
        layout.setSpacing(2)

        self.pinyin_display = QLabel("")
        self.pinyin_display.setStyleSheet("color: #888; font-size: 16px; font-weight: bold;")
        layout.addWidget(self.pinyin_display)

        candidate_area = QWidget()
        candidate_area.setFixedHeight(40)
        candidate_layout = QHBoxLayout(candidate_area)
        candidate_layout.setContentsMargins(0, 0, 0, 0)
        candidate_layout.setSpacing(5)

        self.prev_btn = self._page_button("<")
        self.prev_btn.clicked.connect(self._prev_page)
        self.prev_btn.hide()

        self.next_btn = self._page_button(">")
        self.next_btn.clicked.connect(self._next_page)
        self.next_btn.hide()

        self.candidate_container = QWidget()
        self.candidate_layout = QHBoxLayout(self.candidate_container)
        self.candidate_layout.setContentsMargins(0, 0, 0, 0)
        self.candidate_layout.setSpacing(2)
        self.candidate_layout.addStretch()

        candidate_layout.addWidget(self.prev_btn)
        candidate_layout.addWidget(self.candidate_container, 1)
        candidate_layout.addWidget(self.next_btn)
        layout.addWidget(candidate_area)

    def set_pinyin(self, text: str):
        self.pinyin_display.setText(text)

    def set_candidates(self, candidates: list[str]):
        self.candidates = list(candidates)
        self.candidate_page = 0
        self._update_candidate_ui()

    def current_page_first_candidate(self) -> str:
        start = self.candidate_page * self.page_size
        if start < len(self.candidates):
            return self.candidates[start]
        return ""

    def _page_button(self, text: str) -> QPushButton:
        button = QPushButton(text)
        button.setObjectName("PageBtn")
        return button

    def _update_candidate_ui(self):
        while self.candidate_layout.count() > 1:
            item = self.candidate_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not self.candidates:
            self.prev_btn.hide()
            self.next_btn.hide()
            return

        start = self.candidate_page * self.page_size
        end = start + self.page_size
        for candidate in self.candidates[start:end]:
            button = QPushButton(candidate)
            button.setProperty("class", "CandidateBtn")
            button.setStyleSheet(
                "background: transparent; border: none; color: #1890FF; "
                "font-size: 22px; font-weight: bold;"
            )
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.clicked.connect(lambda checked=False, text=candidate: self.candidateSelected.emit(text))
            self.candidate_layout.insertWidget(self.candidate_layout.count() - 1, button)

        self.prev_btn.setVisible(self.candidate_page > 0)
        self.next_btn.setVisible(len(self.candidates) > end)

    def _next_page(self):
        self.candidate_page += 1
        self._update_candidate_ui()

    def _prev_page(self):
        if self.candidate_page > 0:
            self.candidate_page -= 1
            self._update_candidate_ui()
