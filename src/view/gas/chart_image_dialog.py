from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QDialog, QLabel, QVBoxLayout


class ChartImageDialog(QDialog):
    """气检曲线图查看弹窗。"""

    def __init__(self, pixmap: QPixmap, parent=None):
        super().__init__(parent)
        self.setWindowTitle("曲线图查看")
        self.setModal(True)
        self.resize(980, 720)
        self._build_ui(pixmap)

    def _build_ui(self, pixmap: QPixmap):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)

        image_label = QLabel(self)
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_label.setPixmap(
            pixmap.scaled(
                940,
                680,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )
        layout.addWidget(image_label)
